"""Fixed-5m replay orchestrator for SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1.

This module drives one persistent trader forward through a governed replay slice
using the single existing ``ReplayClock`` (no second, contradictory replay clock)
and reuses the safe skeleton invariants of ``JiangheMarketReplay``:

- only closed 5m bars inside a governed session wake the model (fixed V0.1 policy);
- every step binds observation identity, wake identity and request identity;
- future bars / future mapping / future metadata can never enter a decision;
- model transport is fully mockable and real provider execution stays locked;
- attention-state transitions are validated with the frozen ``validate_transition``.

Restart continuity (Owner gates R1 and R2) is implemented here: state identity is
sealed before close, the runtime/store is reopened from the same project-owned
state, and the reconstructed state must match exactly (no reset).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Protocol, Sequence
from uuid import uuid4

from src.fixed_5m_wake_ledger import (
    Fixed5MWakeLedger,
    GovernedWake,
    WakeLedgerArchive,
    wake_ledger_path_for,
)
from src.jianghe_ai_trader import (
    AttentionMode,
    ConstrainedTradeIntent,
    DecisionAction,
    Direction,
    JiangheDecision,
    JiangheObservation,
    ObservationBar,
    ObservationIdentity,
    ReplayClock,
    StrategyFamily,
    validate_transition,
)
from src.jianghe_response_normalizer import NormalizedJiangheDecision
from src.persistent_deepseek_runtime import PreparedModelRequest
from src.persistent_trader_store import PersistentTraderStore
from src.replay_v0_1_runtime import JOURNAL_WRITE_TRIGGERS, ReplayV01Runtime
from src.replay_v0_1_selector import MEASUREMENT_TRADING_DAYS, ReplaySlice

REPLAY_ORCHESTRATOR_VERSION = "KPE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_ORCHESTRATOR_V0_1"
PHASE_BURN_IN = "BURN_IN"
PHASE_MEASUREMENT = "MEASUREMENT"
ACTIVE_STATE_RESTART_COVERAGE_OBSERVED = "OBSERVED"
ACTIVE_STATE_RESTART_COVERAGE_NOT_OBSERVED = "NOT_OBSERVED"
ACTIVE_STATE_RESTART_COVERAGE_NOT_ARMED = "NOT_ARMED"
ACTIVE_ATTENTION_MODES = frozenset(
    {AttentionMode.WATCH, AttentionMode.CANDIDATE, AttentionMode.IN_POSITION}
)
GOVERNED_TRADING_ONLY_INTENT = "ENTER_INTENT_ONLY_NO_EXECUTION_CLAIM"


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _aware(value: datetime, field_name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value


def _iso(value: datetime) -> str:
    return _aware(value, "datetime").astimezone(timezone.utc).isoformat(timespec="microseconds")


def _non_empty(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be non-empty")
    return value


@dataclass(frozen=True)
class GovernedWakeStep:
    """One governed 5m wake: the newly closed 5m bar plus its causal context."""

    trading_day: date
    session_identity: str
    wake_bar: ObservationBar
    context_bars: tuple[ObservationBar, ...] = ()

    def __post_init__(self) -> None:
        if self.wake_bar.timeframe != "5m":
            raise ValueError("only a newly closed 5m bar may produce a governed wake")
        if not self.wake_bar.is_closed:
            raise ValueError("a governed wake requires a closed 5m bar")
        _aware(self.wake_bar.available_at, "wake_bar.available_at")
        if self.wake_bar.available_at < self.wake_bar.close_time:
            raise ValueError("wake bar available_at cannot precede its close_time")


class ReplayModelTransport(Protocol):
    """Model transport seam. Real provider execution stays locked; only mocks pass."""

    provider_identity: str
    mock: bool

    def execute(self, request: PreparedModelRequest) -> str:
        """Return raw model response text for an already-prepared request."""
        ...


class NoProviderTransport:
    """Fail-closed default transport: no provider call can ever be made."""

    provider_identity = "NO_PROVIDER_LOCKED"
    mock = False

    def execute(self, request: PreparedModelRequest) -> str:
        raise RuntimeError("no provider transport is admitted in replay V0.1 offline engineering")


class SyntheticScriptedTransport:
    """Deterministic mock transport. It is the only transport admitted to tests."""

    provider_identity = "NO_PROVIDER_SYNTHETIC_MOCK"
    mock = True

    def __init__(self, responses: Iterable[str] | None = None) -> None:
        self._responses = list(responses or ())
        self.calls: list[PreparedModelRequest] = []

    def execute(self, request: PreparedModelRequest) -> str:
        if not self._responses:
            raise RuntimeError("scripted mock transport has no remaining response")
        self.calls.append(request)
        return self._responses.pop(0)


@dataclass(frozen=True)
class ReplayStepBinding:
    sequence: int
    trading_day: date
    session_identity: str
    close_time: datetime
    wake_identity: str
    observation_identity: str
    request_id: str
    decision_identity: str
    attention_mode_before: str
    attention_mode_after: str
    active_state_restart_triggered: bool = False


@dataclass(frozen=True)
class ReplayResult:
    orchestrator_version: str
    slice_identity: str
    trader_identity: str
    step_count: int
    wake_count: int
    request_count: int
    r1_restart_verified: bool
    active_state_restart_coverage: str
    r2_restart_occurred: bool
    state_identity: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "orchestrator_version": self.orchestrator_version,
            "slice_identity": self.slice_identity,
            "trader_identity": self.trader_identity,
            "step_count": self.step_count,
            "wake_count": self.wake_count,
            "request_count": self.request_count,
            "r1_restart_verified": self.r1_restart_verified,
            "active_state_restart_coverage": self.active_state_restart_coverage,
            "r2_restart_occurred": self.r2_restart_occurred,
            "state_identity": self.state_identity,
        }


def _project_to_jianghe_decision(normalized: NormalizedJiangheDecision) -> JiangheDecision:
    """Mechanical projection; no research-semantic invention."""
    trade_intent = None
    if normalized.action is DecisionAction.ENTER:
        trade_intent = ConstrainedTradeIntent(
            direction=normalized.direction,
            intent_type=GOVERNED_TRADING_ONLY_INTENT,
            rationale_reference=normalized.rationale or normalized.decision_state,
        )
    return JiangheDecision(
        attention_mode=normalized.attention_mode,
        family=normalized.family,
        direction=normalized.direction,
        action=normalized.action,
        uncertainty=normalized.decision_state,
        watch_regions=(),
        invalidation=None,
        next_review=None,
        referenced_jianghe_claims=tuple(normalized.principle_references),
        referenced_cases=(),
        rationale=normalized.rationale,
        trade_intent=trade_intent,
    )


class IntentPositionLifecycle:
    """Minimal project-owned intent-position decision-state record.

    The authoritative current decision state is ``DS_WORKING_MEMORY.attention_mode``
    (persisted in the store).  This helper writes an append-only audit event per
    decision so the legal decision-state sequence is reconstructable.  It never
    claims a fill, slippage, position, PnL or execution realism.
    """

    EVENT_KIND = "REPLAY_INTENT_POSITION"

    def __init__(self, store: PersistentTraderStore) -> None:
        self._store = store

    def record_decision(
        self,
        *,
        trading_day: date,
        session_identity: str,
        observation_identity: str,
        wake_identity: str,
        request_id: str,
        decision: NormalizedJiangheDecision,
        before_mode: AttentionMode,
        after_mode: AttentionMode,
        occurred_at: datetime,
    ) -> str:
        _non_empty(observation_identity, "observation_identity")
        _non_empty(wake_identity, "wake_identity")
        _non_empty(request_id, "request_id")
        _non_empty(session_identity, "session_identity")
        if not isinstance(trading_day, date):
            raise ValueError("trading_day must be a date")
        _aware(occurred_at, "occurred_at")
        event_id = f"intent-pos-{_hash((observation_identity, request_id, wake_identity))}"
        payload = {
            "trading_day": trading_day.isoformat(),
            "session_identity": session_identity,
            "observation_identity": observation_identity,
            "wake_identity": wake_identity,
            "request_id": request_id,
            "decision_identity": decision.identity,
            "action": decision.action.value,
            "direction": decision.direction.value,
            "family": decision.family.value,
            "attention_mode_before": before_mode.value,
            "attention_mode_after": after_mode.value,
            "execution_claim": False,
            "paper_fill_claimed": False,
            "intent_only": True,
        }
        self._store.append_audit(
            event_id=event_id,
            occurred_at=occurred_at,
            event_kind=self.EVENT_KIND,
            observation_identity=observation_identity,
            request_id=request_id,
            payload=payload,
        )
        return event_id

    @classmethod
    def list_events(cls, store: PersistentTraderStore) -> tuple[dict[str, Any], ...]:
        return tuple(
            dict(event.payload)
            for event in store.list_audit()
            if event.event_kind == cls.EVENT_KIND
        )


REPLAY_CONTROL_EVENT_KINDS = frozenset(
    {
        "REPLAY_STATE_SEALED",
        "REPLAY_RESTART_VERIFIED",
        "REPLAY_ACTIVE_STATE_RESTART_COVERAGE",
        "REPLAY_SESSION_END",
        "REPLAY_FINALIZED",
    }
)


class ReplayStateSealer:
    """Deterministic state-identity seal/verify for restart continuity."""

    VERSION = "KPE_REPLAY_STATE_SEAL_V0_1"

    @classmethod
    def compute_state_identity(
        cls,
        *,
        runtime: ReplayV01Runtime,
        slice_: ReplaySlice,
        wake_archive_path: str | Path | None = None,
        exclude_event_kinds: frozenset[str] = frozenset(),
    ) -> str:
        exported = runtime.portable_export()
        if exclude_event_kinds:
            exported = dict(exported)
            exported["audit"] = [
                event
                for event in exported["audit"]
                if event.get("event_kind") not in exclude_event_kinds
            ]
        wake_payload = None
        if wake_archive_path is not None and Path(wake_archive_path).exists():
            wake_payload = WakeLedgerArchive(wake_archive_path).portable_export()
        return _hash(
            {
                "seal_version": cls.VERSION,
                "slice_identity": slice_.identity,
                "trader_identity": runtime.trader_identity.identity,
                "runtime_export": exported,
                "wake_archive": wake_payload,
            }
        )

    @classmethod
    def assert_continuity(
        cls,
        *,
        sealed_identity: str,
        runtime: ReplayV01Runtime,
        slice_: ReplaySlice,
        wake_archive_path: str | Path | None = None,
    ) -> None:
        current = cls.compute_state_identity(
            runtime=runtime, slice_=slice_, wake_archive_path=wake_archive_path
        )
        if current != sealed_identity:
            raise ValueError(
                "restart continuity failed: state identity drifted "
                f"(sealed={sealed_identity}, current={current})"
            )


RuntimeFactory = Callable[[Callable[[], datetime]], ReplayV01Runtime]


class ReplayV01Orchestrator:
    """Forward-only orchestrator for the fixed-5m replay lifecycle."""

    def __init__(
        self,
        *,
        runtime_factory: RuntimeFactory,
        clock: ReplayClock,
        slice_: ReplaySlice,
        transport: ReplayModelTransport,
        state_dir: str | Path,
        retrieval_query: str = "current causal market state and key locations",
        r2_active_restart_measurement_day: int = 4,
    ) -> None:
        if not transport.mock:
            raise ValueError("replay V0.1 admits only mock model transport; provider stays locked")
        if not callable(runtime_factory):
            raise TypeError("runtime_factory must be callable")
        if not isinstance(clock, ReplayClock):
            raise TypeError("orchestrator requires the single existing ReplayClock")
        if not isinstance(slice_, ReplaySlice):
            raise TypeError("orchestrator requires a sealed ReplaySlice")
        if not isinstance(r2_active_restart_measurement_day, int) or r2_active_restart_measurement_day < 1:
            raise ValueError("R2 active-state restart measurement day must be >= 1")
        self._runtime_factory = runtime_factory
        self._clock = clock
        self._slice = slice_
        self._transport = transport
        self._state_dir = Path(state_dir)
        self._state_dir.mkdir(parents=True, exist_ok=True)
        self._retrieval_query = _non_empty(retrieval_query, "retrieval_query")
        self._r2_active_restart_measurement_day = r2_active_restart_measurement_day
        self._wake_db_path = wake_ledger_path_for(self._state_dir)
        self._runtime = runtime_factory(lambda: self._clock.current_time)
        self._ledger: Fixed5MWakeLedger | None = None
        self._intent_lifecycle = IntentPositionLifecycle(self._runtime.store)
        self._steps: list[ReplayStepBinding] = []
        self._session_identity: str | None = None
        self._session_phase: str | None = None
        self._session_trading_day: date | None = None
        self._session_replay_day_index: int | None = None
        self._current_replay_day_index = -1
        self._r1_restart_verified = False
        self._r2_restart_occurred = False
        self._r2_armed = False
        self._r2_coverage = ACTIVE_STATE_RESTART_COVERAGE_NOT_ARMED
        self._sealed_identity: str | None = None

    @property
    def runtime(self) -> ReplayV01Runtime:
        return self._runtime

    @property
    def clock(self) -> ReplayClock:
        return self._clock

    @property
    def wake_ledger(self) -> Fixed5MWakeLedger | None:
        return self._ledger

    @property
    def state_dir(self) -> Path:
        return self._state_dir

    def begin_session(
        self,
        *,
        phase: str,
        trading_day: date,
        replay_day_index: int,
        session_identity: str,
        steps: Sequence[GovernedWakeStep],
    ) -> None:
        """Open one governed session's wake ledger with its expected 5m schedule."""
        if phase not in (PHASE_BURN_IN, PHASE_MEASUREMENT):
            raise ValueError("governed session phase must be BURN_IN or MEASUREMENT")
        if not isinstance(trading_day, date):
            raise ValueError("trading_day must be a date")
        _non_empty(session_identity, "session_identity")
        all_days = self._slice.burn_in_days + self._slice.measurement_days
        if not (0 <= replay_day_index < len(all_days)):
            raise ValueError("replay_day_index is outside the sealed replay window")
        if trading_day != all_days[replay_day_index]:
            raise ValueError(
                f"trading_day {trading_day.isoformat()} does not match the sealed slice "
                f"day {all_days[replay_day_index].isoformat()} at index {replay_day_index}"
            )
        if replay_day_index > self._current_replay_day_index + 1:
            raise ValueError(
                "replay day index cannot skip a trading day; "
                f"current={self._current_replay_day_index}, requested={replay_day_index}"
            )
        if replay_day_index < self._current_replay_day_index:
            raise ValueError("replay day index cannot regress")
        if phase == PHASE_BURN_IN and replay_day_index >= len(self._slice.burn_in_days):
            raise ValueError("burn-in session cannot reference a measurement replay day")
        if self._ledger is not None:
            raise ValueError("previous governed session wake ledger is still open")
        if replay_day_index > self._current_replay_day_index:
            self._current_replay_day_index = replay_day_index
        steps_tuple = tuple(steps)
        if not steps_tuple:
            raise ValueError("a governed session must contain at least one 5m wake step")
        expected_phase = (
            PHASE_BURN_IN
            if replay_day_index < len(self._slice.burn_in_days)
            else PHASE_MEASUREMENT
        )
        if phase != expected_phase:
            raise ValueError("governed session phase does not match the replay day index")
        schedule = tuple(step.wake_bar.close_time for step in steps_tuple)
        self._ledger = Fixed5MWakeLedger(
            wake_ledger_path_for(self._state_dir),
            trader_identity=self._runtime.trader_identity.identity,
            session_identity=session_identity,
            schedule_5m_closes=schedule,
        )
        self._session_identity = session_identity
        self._session_phase = phase
        self._session_trading_day = trading_day
        self._session_replay_day_index = replay_day_index
        if phase == PHASE_MEASUREMENT and replay_day_index >= (
            len(self._slice.burn_in_days) + self._r2_active_restart_measurement_day - 1
        ):
            self._r2_armed = True

    def run_wake_step(self, step: GovernedWakeStep) -> ReplayStepBinding:
        """Process exactly one governed 5m wake and bind all step identities."""
        if self._ledger is None:
            raise ValueError("no governed session is open; call begin_session first")
        _non_empty(step.session_identity, "step.session_identity")
        if step.session_identity != self._session_identity:
            raise ValueError("wake step session does not match the open governed session")
        if step.trading_day != self._session_trading_day:
            raise ValueError("wake step trading day does not match the open governed session")
        if self._ledger.is_closed():
            raise ValueError("governed session wake ledger is closed; cannot add wakes")
        decision_time = _aware(step.wake_bar.available_at, "wake_bar.available_at")
        if decision_time < step.wake_bar.close_time:
            raise ValueError("wake decision_time cannot precede the closed bar close_time")
        self._reject_future_bars(step.context_bars, decision_time)
        # Single forward-only ReplayClock (reused; no second contradictory clock).
        self._clock.advance_to(decision_time)
        wake = self._ledger.register_closed_5m(step.wake_bar.close_time)
        observation = self._build_observation(decision_time=decision_time, step=step)
        request = self._runtime.prepare_model_request(
            observation=observation, retrieval_query=self._retrieval_query
        )
        self._ledger.bind_request(wake.wake_identity, request.request_id, retry_count=0)
        raw_response = self._transport.execute(request)
        decision = self._runtime.record_model_response(
            request_id=request.request_id, raw_response=raw_response
        )
        before_mode = self._runtime.store.load_working_memory().attention_mode
        jianghe_decision = _project_to_jianghe_decision(decision)
        after_mode = validate_transition(before_mode, jianghe_decision)
        self._intent_lifecycle.record_decision(
            trading_day=step.trading_day,
            session_identity=step.session_identity,
            observation_identity=observation.identity.identity,
            wake_identity=wake.wake_identity,
            request_id=request.request_id,
            decision=decision,
            before_mode=before_mode,
            after_mode=after_mode,
            occurred_at=decision_time,
        )
        self._apply_working_memory(
            observation_identity=observation.identity.identity,
            jianghe_decision=jianghe_decision,
            after_mode=after_mode,
            occurred_at=decision_time,
        )
        restart_triggered = False
        if self._r2_armed and not self._r2_restart_occurred and after_mode in ACTIVE_ATTENTION_MODES:
            self._r2_restart_occurred = True
            self._r2_coverage = ACTIVE_STATE_RESTART_COVERAGE_OBSERVED
            self._append_audit_replay_event(
                event_kind="REPLAY_ACTIVE_STATE_RESTART_COVERAGE",
                payload={
                    "coverage": self._r2_coverage,
                    "trigger_action": decision.action.value,
                    "trigger_attention_mode": after_mode.value,
                    "trading_day": step.trading_day.isoformat(),
                    "session_identity": step.session_identity,
                },
                observation_identity=observation.identity.identity,
                request_id=request.request_id,
            )
            self.restart()
            restart_triggered = True
        binding = ReplayStepBinding(
            sequence=len(self._steps),
            trading_day=step.trading_day,
            session_identity=step.session_identity,
            close_time=wake.close_time,
            wake_identity=wake.wake_identity,
            observation_identity=observation.identity.identity,
            request_id=request.request_id,
            decision_identity=decision.identity,
            attention_mode_before=before_mode.value,
            attention_mode_after=after_mode.value,
            active_state_restart_triggered=restart_triggered,
        )
        self._steps.append(binding)
        return binding

    def end_session(self) -> None:
        """Close the governed session and verify wake completeness and binding."""
        if self._ledger is None:
            raise ValueError("no governed session is open")
        self._ledger.close_session()
        self._runtime.append_journal(
            entry_id=f"session-end-{self._session_identity}",
            body=(
                f"governed session {self._session_identity} ended with "
                f"{len(self._ledger.list_wakes())} closed-5m wakes; every wake admitted "
                "exactly one request with retry count zero."
            ),
            trigger="END_OF_SESSION",
            observation_identity=self._steps[-1].observation_identity if self._steps else None,
            tags=("V0_1_REPLAY", f"SESSION:{self._session_identity}"),
        )
        self._append_audit_replay_event(
            event_kind="REPLAY_SESSION_END",
            payload={
                "session_identity": self._session_identity,
                "phase": self._session_phase,
                "trading_day": self._session_trading_day.isoformat(),
                "replay_day_index": self._session_replay_day_index,
                "wake_count": len(self._ledger.list_wakes()),
            },
        )
        self._ledger = None
        self._session_identity = None
        self._session_phase = None
        self._session_trading_day = None
        self._session_replay_day_index = None

    def seal_state_identity(self) -> str:
        """Seal/export the current state identity before a restart boundary."""
        # The seal audit event must be persisted before the identity is computed so
        # that a reopen recomputes the identical identity (restart continuity).
        self._append_audit_replay_event(
            event_kind="REPLAY_STATE_SEALED",
            payload={"session_identity": self._session_identity},
        )
        identity = ReplayStateSealer.compute_state_identity(
            runtime=self._runtime,
            slice_=self._slice,
            wake_archive_path=self._wake_db_path,
        )
        self._sealed_identity = identity
        return identity

    def restart(self) -> str:
        """R1/R2 restart: seal, close, reopen from the same state, prove continuity.

        Works both at a phase boundary (no governed session open) and mid-session
        (the current session's wake ledger is reopened from the same state).
        """
        sealed = self.seal_state_identity()
        self._runtime.close()
        self._runtime = self._runtime_factory(lambda: self._clock.current_time)
        if self._ledger is not None:
            self._ledger = Fixed5MWakeLedger(
                self._wake_db_path,
                trader_identity=self._runtime.trader_identity.identity,
                session_identity=self._session_identity or "",
                schedule_5m_closes=self._ledger.schedule,
            )
        self._intent_lifecycle = IntentPositionLifecycle(self._runtime.store)
        ReplayStateSealer.assert_continuity(
            runtime=self._runtime,
            slice_=self._slice,
            wake_archive_path=self._wake_db_path,
            sealed_identity=sealed,
        )
        self._append_audit_replay_event(
            event_kind="REPLAY_RESTART_VERIFIED",
            payload={
                "state_identity": sealed,
                "session_identity": self._session_identity,
                "restart_continuity": "VERIFIED",
            },
        )
        return sealed

    def phase_boundary_restart(self) -> str:
        """R1: mandatory restart between burn-in day 2 and measurement."""
        sealed = self.restart()
        self._r1_restart_verified = True
        return sealed

    def active_state_restart_coverage(self) -> str:
        return self._r2_coverage

    def finalize(self) -> ReplayResult:
        """Finalize the replay and record R2 NOT_OBSERVED when the window had no trigger."""
        if self._ledger is not None:
            raise ValueError("cannot finalize while a governed session is still open")
        if self._r2_armed and not self._r2_restart_occurred:
            self._r2_coverage = ACTIVE_STATE_RESTART_COVERAGE_NOT_OBSERVED
            self._append_audit_replay_event(
                event_kind="REPLAY_ACTIVE_STATE_RESTART_COVERAGE",
                payload={"coverage": self._r2_coverage, "condition_window": "AFTER_MEASUREMENT_DAY_3"},
            )
        state_identity = ReplayStateSealer.compute_state_identity(
            runtime=self._runtime,
            slice_=self._slice,
            wake_archive_path=self._wake_db_path,
            exclude_event_kinds=REPLAY_CONTROL_EVENT_KINDS,
        )
        result = ReplayResult(
            orchestrator_version=REPLAY_ORCHESTRATOR_VERSION,
            slice_identity=self._slice.identity,
            trader_identity=self._runtime.trader_identity.identity,
            step_count=len(self._steps),
            wake_count=len(self._steps),
            request_count=len(self._steps),
            r1_restart_verified=self._r1_restart_verified,
            active_state_restart_coverage=self._r2_coverage,
            r2_restart_occurred=self._r2_restart_occurred,
            state_identity=state_identity,
        )
        self._append_audit_replay_event(
            event_kind="REPLAY_FINALIZED",
            payload=result.to_payload(),
        )
        return result

    def list_step_bindings(self) -> tuple[ReplayStepBinding, ...]:
        return tuple(self._steps)

    def _build_observation(
        self, *, decision_time: datetime, step: GovernedWakeStep
    ) -> JiangheObservation:
        mapping_identity = self._slice.mapping_identities[self._session_replay_day_index or 0]
        timeframes = {bar.timeframe for bar in step.context_bars}
        if not timeframes.issuperset({"4H", "1H", "15m", "5m"}):
            raise ValueError(
                "governed observation must expose the active stack 4H/1H/15m/5m; "
                f"got {sorted(timeframes)}"
            )
        identity = ObservationIdentity(
            decision_time=decision_time,
            exchange_time=decision_time,
            product=self._slice.product,
            concrete_contract=self._slice.concrete_contract,
            mapping_identity=mapping_identity,
            session_identity=self._session_identity or "",
        )
        return JiangheObservation(identity=identity, bars=step.context_bars)

    def _apply_working_memory(
        self,
        *,
        observation_identity: str,
        jianghe_decision: JiangheDecision,
        after_mode: AttentionMode,
        occurred_at: datetime,
    ) -> None:
        mutations: tuple[tuple[str, object, str], ...] = (
            ("attention_mode", after_mode, "V0_1_GOVERNED_STATE_TRANSITION"),
            ("last_meaningful_decision", jianghe_decision.action.value, "V0_1_GOVERNED_DECISION"),
            ("transition_reason", jianghe_decision.rationale or jianghe_decision.uncertainty, "V0_1_GOVERNED_DECISION"),
            ("directional_bias", jianghe_decision.direction, "V0_1_GOVERNED_DECISION"),
            ("active_family_hypothesis", jianghe_decision.family, "V0_1_GOVERNED_DECISION"),
        )
        for field_name, new_value, reason in mutations:
            self._runtime.mutate_working_memory(
                field_name=field_name,
                new_value=new_value,
                reason=reason,
                observation_identity=observation_identity,
            )

    def _reject_future_bars(
        self, bars: Sequence[ObservationBar], decision_time: datetime
    ) -> None:
        for bar in bars:
            if bar.available_at > decision_time:
                raise ValueError(
                    f"future-bar leak rejected: {bar.timeframe} bar available_at "
                    f"{_iso(bar.available_at)} exceeds decision_time {_iso(decision_time)}"
                )
            if bar.close_time > decision_time:
                raise ValueError(
                    f"future-bar leak rejected: {bar.timeframe} bar close_time "
                    f"{_iso(bar.close_time)} exceeds decision_time {_iso(decision_time)}"
                )

    def _append_audit_replay_event(
        self,
        *,
        event_kind: str,
        payload: Mapping[str, Any],
        observation_identity: str | None = None,
        request_id: str | None = None,
    ) -> None:
        self._runtime.store.append_audit(
            event_id=f"replay-{event_kind.lower()}-{uuid4().hex}",
            occurred_at=self._clock.current_time,
            event_kind=event_kind,
            observation_identity=observation_identity,
            request_id=request_id,
            payload=dict(payload),
        )


__all__ = [
    "ACTIVE_STATE_RESTART_COVERAGE_NOT_ARMED",
    "ACTIVE_STATE_RESTART_COVERAGE_NOT_OBSERVED",
    "ACTIVE_STATE_RESTART_COVERAGE_OBSERVED",
    "ACTIVE_ATTENTION_MODES",
    "GOVERNED_TRADING_ONLY_INTENT",
    "REPLAY_CONTROL_EVENT_KINDS",
    "GovernedWakeStep",
    "IntentPositionLifecycle",
    "NoProviderTransport",
    "PHASE_BURN_IN",
    "PHASE_MEASUREMENT",
    "REPLAY_ORCHESTRATOR_VERSION",
    "ReplayModelTransport",
    "ReplayResult",
    "ReplayStateSealer",
    "ReplayStepBinding",
    "ReplayV01Orchestrator",
    "RuntimeFactory",
    "SyntheticScriptedTransport",
]

"""Full-lifecycle mock rehearsal for SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1.

Drives already-governed causal wake steps through the accepted V0.1 orchestrator
for the complete sealed 2-day burn-in + 20-day measurement window. No provider
transport capability exists here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from itertools import groupby
from typing import Iterable

from src.persistent_deepseek_runtime import PreparedModelRequest
from src.replay_v0_1_orchestrator import (
    ACTIVE_STATE_RESTART_COVERAGE_NOT_OBSERVED,
    ACTIVE_STATE_RESTART_COVERAGE_OBSERVED,
    GovernedWakeStep,
    PHASE_BURN_IN,
    PHASE_MEASUREMENT,
    ReplayResult,
    ReplayV01Orchestrator,
)
from src.replay_v0_1_selector import BURN_IN_TRADING_DAYS, ReplaySlice

FULL_MOCK_DRY_RUN_VERSION = "KPE_REPLAY_V0_1_FULL_MOCK_DRY_RUN_V0_1"
MOCK_PROVIDER_IDENTITY = "NO_PROVIDER_DETERMINISTIC_WAIT_MOCK_V0_1"


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


class DeterministicWaitTransport:
    provider_identity = MOCK_PROVIDER_IDENTITY
    mock = True

    def __init__(self) -> None:
        self.calls: list[PreparedModelRequest] = []

    def execute(self, request: PreparedModelRequest) -> str:
        if not isinstance(request, PreparedModelRequest):
            raise TypeError("mock transport requires PreparedModelRequest")
        self.calls.append(request)
        return json.dumps({
            "schema_version": "JIANGHE_RUNTIME_RESPONSE_V0_2",
            "family": "NONE",
            "action": "WAIT",
            "direction": "NONE",
            "attention_mode": "SCAN",
            "decision_state": "mock_dry_run_wait",
            "rationale": "Deterministic offline lifecycle rehearsal; no provider call occurred.",
            "declared_unknown": [],
            "principle_references": [],
            "source_references": [],
            "numeric_claims": [],
            "current_market_hypothesis": None,
            "timeframe_trend_view": [],
            "key_location_hypotheses": [],
            "expected_trigger": None,
            "invalidation_hypothesis": None,
            "open_questions": [],
        }, ensure_ascii=False, sort_keys=True)


@dataclass(frozen=True)
class FullMockDryRunSummary:
    version: str
    slice_identity: str
    trader_identity: str
    replay_day_count: int
    burn_in_day_count: int
    measurement_day_count: int
    governed_session_count: int
    step_count: int
    wake_count: int
    request_count: int
    mock_transport_call_count: int
    r1_restart_verified: bool
    r2_restart_occurred: bool
    active_state_restart_coverage: str
    final_state_identity: str
    provider_call_authorized: bool = False
    result: str = "PASS"
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if (self.replay_day_count, self.burn_in_day_count, self.measurement_day_count) != (22, 2, 20):
            raise ValueError("full V0.1 mock dry run must bind exactly 2 burn-in + 20 measurement days")
        if self.step_count <= 0 or self.governed_session_count <= 0:
            raise ValueError("full V0.1 mock dry run must contain governed sessions and wake steps")
        if not (self.step_count == self.wake_count == self.request_count == self.mock_transport_call_count):
            raise ValueError("full V0.1 dry run requires exact step=wake=request=mock-call accounting")
        if self.r1_restart_verified is not True:
            raise ValueError("full V0.1 dry run requires the mandatory R1 restart")
        if self.active_state_restart_coverage not in {ACTIVE_STATE_RESTART_COVERAGE_OBSERVED, ACTIVE_STATE_RESTART_COVERAGE_NOT_OBSERVED}:
            raise ValueError("full V0.1 dry run must resolve R2 coverage")
        if self.provider_call_authorized is not False or self.result != "PASS":
            raise ValueError("mock dry run summary must be PASS with provider locked")
        object.__setattr__(self, "identity", _hash(self.to_payload(include_identity=False)))

    def to_payload(self, *, include_identity: bool = True) -> dict[str, object]:
        payload = {
            "version": self.version,
            "slice_identity": self.slice_identity,
            "trader_identity": self.trader_identity,
            "replay_day_count": self.replay_day_count,
            "burn_in_day_count": self.burn_in_day_count,
            "measurement_day_count": self.measurement_day_count,
            "governed_session_count": self.governed_session_count,
            "step_count": self.step_count,
            "wake_count": self.wake_count,
            "request_count": self.request_count,
            "mock_transport_call_count": self.mock_transport_call_count,
            "r1_restart_verified": self.r1_restart_verified,
            "r2_restart_occurred": self.r2_restart_occurred,
            "active_state_restart_coverage": self.active_state_restart_coverage,
            "final_state_identity": self.final_state_identity,
            "provider_call_authorized": self.provider_call_authorized,
            "result": self.result,
        }
        if include_identity:
            payload["identity"] = self.identity
        return payload


def _ordered_steps_by_day(*, slice_: ReplaySlice, steps: Iterable[GovernedWakeStep]) -> tuple[tuple[GovernedWakeStep, ...], ...]:
    if not isinstance(slice_, ReplaySlice):
        raise TypeError("full mock dry run requires a sealed ReplaySlice")
    all_days = slice_.burn_in_days + slice_.measurement_days
    if len(all_days) != 22:
        raise ValueError("full mock dry run requires the complete 22-day V0.1 slice")
    raw = tuple(steps)
    if not raw:
        raise ValueError("full mock dry run requires governed wake steps")
    expected_set = set(all_days)
    actual_set = {step.trading_day for step in raw}
    missing = expected_set - actual_set
    extra = actual_set - expected_set
    if missing or extra:
        raise ValueError("full mock dry run step-day coverage disagrees with sealed slice: "
                         f"missing={sorted(day.isoformat() for day in missing)}, extra={sorted(day.isoformat() for day in extra)}")
    by_day = []
    previous_time = None
    for day in all_days:
        day_steps = tuple(step for step in raw if step.trading_day == day)
        ordered = tuple(sorted(day_steps, key=lambda step: step.wake_bar.available_at))
        if day_steps != ordered:
            raise ValueError("full mock dry run input steps must already be in causal order")
        if len({step.wake_bar.available_at for step in ordered}) != len(ordered):
            raise ValueError("governed wake times must be unique within each replay day")
        for step in ordered:
            current = step.wake_bar.available_at
            if previous_time is not None and current <= previous_time:
                raise ValueError("full mock dry run wake timeline must be strictly forward-only")
            previous_time = current
        by_day.append(ordered)
    if sum(len(items) for items in by_day) != len(raw):
        raise ValueError("full mock dry run contains unaccounted governed steps")
    return tuple(by_day)


def drive_full_mock_replay(*, orchestrator: ReplayV01Orchestrator, slice_: ReplaySlice,
                           steps: Iterable[GovernedWakeStep], transport: DeterministicWaitTransport) -> FullMockDryRunSummary:
    if not isinstance(orchestrator, ReplayV01Orchestrator):
        raise TypeError("orchestrator must be ReplayV01Orchestrator")
    if not isinstance(transport, DeterministicWaitTransport):
        raise TypeError("full mock dry run requires DeterministicWaitTransport")
    day_groups = _ordered_steps_by_day(slice_=slice_, steps=steps)
    governed_session_count = 0
    total_steps = 0
    for day_index, day_steps in enumerate(day_groups):
        phase = PHASE_BURN_IN if day_index < BURN_IN_TRADING_DAYS else PHASE_MEASUREMENT
        for session_identity, session_iter in groupby(day_steps, key=lambda step: step.session_identity):
            session_steps = tuple(session_iter)
            orchestrator.begin_session(phase=phase, trading_day=day_steps[0].trading_day,
                                       replay_day_index=day_index, session_identity=session_identity,
                                       steps=session_steps)
            for step in session_steps:
                orchestrator.run_wake_step(step)
                total_steps += 1
            orchestrator.end_session()
            governed_session_count += 1
        if day_index == BURN_IN_TRADING_DAYS - 1:
            orchestrator.phase_boundary_restart()
    result: ReplayResult = orchestrator.finalize()
    if result.step_count != total_steps or len(transport.calls) != total_steps:
        raise ValueError("full dry-run accounting drift")
    return FullMockDryRunSummary(
        version=FULL_MOCK_DRY_RUN_VERSION,
        slice_identity=slice_.identity,
        trader_identity=result.trader_identity,
        replay_day_count=len(day_groups), burn_in_day_count=len(slice_.burn_in_days),
        measurement_day_count=len(slice_.measurement_days), governed_session_count=governed_session_count,
        step_count=result.step_count, wake_count=result.wake_count, request_count=result.request_count,
        mock_transport_call_count=len(transport.calls), r1_restart_verified=result.r1_restart_verified,
        r2_restart_occurred=result.r2_restart_occurred,
        active_state_restart_coverage=result.active_state_restart_coverage,
        final_state_identity=result.state_identity)


__all__ = ["DeterministicWaitTransport", "FULL_MOCK_DRY_RUN_VERSION", "FullMockDryRunSummary",
           "MOCK_PROVIDER_IDENTITY", "drive_full_mock_replay"]

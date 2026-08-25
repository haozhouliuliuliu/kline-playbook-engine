"""Deterministic, outcome-blind integrity gates for replay V0.1.

Every gate is project-owned, fail-closed, deterministic and free of any PnL /
profit / win-rate / outcome dependency.  Gates reconstruct their evidence from
the append-only audit trail, the wake ledger archive and the persisted working
memory, so a completed replay is auditable from its own state alone.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from src.fixed_5m_wake_ledger import WakeLedgerArchive
from src.jianghe_ai_trader import (
    AttentionMode,
    ConstrainedTradeIntent,
    DecisionAction,
    Direction,
    JiangheDecision,
    StrategyFamily,
    validate_transition,
)
from src.replay_v0_1_orchestrator import (
    REPLAY_CONTROL_EVENT_KINDS,
    ReplayResult,
    ReplayStateSealer,
)
from src.replay_v0_1_runtime import ReplayV01Runtime
from src.replay_v0_1_selector import ReplaySlice
from src.persistent_trader_store import HYPOTHESIS_STATUSES

INTEGRITY_AUDITOR_VERSION = "KPE_REPLAY_INTEGRITY_AUDITOR_V0_1"
FORBIDDEN_POLICY_WRITE_KINDS = frozenset(
    {"POLICY_PROMOTION", "CANON_WRITE", "JIANGHE_CANON_WRITE", "VALIDATED_POLICY_WRITE"}
)


def _parse_dt(value: object, field_name: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty ISO datetime")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return parsed


def _decision_from_payload(
    *,
    action: str,
    direction: str,
    family: str,
    attention_mode: str,
) -> JiangheDecision:
    decision_action = DecisionAction(action)
    decision_direction = Direction(direction)
    trade_intent = None
    if decision_action is DecisionAction.ENTER:
        trade_intent = ConstrainedTradeIntent(
            direction=decision_direction,
            intent_type="ENTER_INTENT_ONLY_NO_EXECUTION_CLAIM",
            rationale_reference="reconstructed for transition validation",
        )
    return JiangheDecision(
        attention_mode=AttentionMode(attention_mode),
        family=StrategyFamily(family),
        direction=decision_direction,
        action=decision_action,
        uncertainty="integrity-reconstructed decision state",
        watch_regions=(),
        invalidation=None,
        next_review=None,
        referenced_jianghe_claims=(),
        referenced_cases=(),
        rationale="integrity-reconstructed",
        trade_intent=trade_intent,
    )


@dataclass(frozen=True)
class IntegrityCheckResult:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class IntegrityReport:
    checks: tuple[IntegrityCheckResult, ...]
    auditor_version: str = INTEGRITY_AUDITOR_VERSION

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    def failed_checks(self) -> tuple[IntegrityCheckResult, ...]:
        return tuple(check for check in self.checks if not check.passed)

    def assert_passed(self) -> None:
        failed = self.failed_checks()
        if failed:
            detail = "; ".join(f"{check.name}: {check.detail}" for check in failed)
            raise ValueError(f"replay integrity gate failed: {detail}")

    def to_payload(self) -> dict[str, Any]:
        return {
            "auditor_version": self.auditor_version,
            "passed": self.passed,
            "checks": [
                {"name": check.name, "passed": check.passed, "detail": check.detail}
                for check in self.checks
            ],
        }


class ReplayIntegrityAuditor:
    """Runs the full battery of V0.1 lifecycle integrity gates."""

    def __init__(
        self,
        *,
        runtime: ReplayV01Runtime,
        slice_: ReplaySlice,
        wake_archive: WakeLedgerArchive,
        result: ReplayResult | None = None,
    ) -> None:
        self._runtime = runtime
        self._slice = slice_
        self._archive = wake_archive
        self._result = result
        self._audit = runtime.store.list_audit()

    def audit(self) -> IntegrityReport:
        checks: list[IntegrityCheckResult] = []
        checks.append(self._check_future_leakage())
        checks.append(self._check_duplicate_missing_wake())
        checks.append(self._check_duplicate_missing_request())
        checks.append(self._check_identity_drift())
        checks.append(self._check_clock_regression())
        checks.append(self._check_restart_continuity())
        checks.append(self._check_memory_reset())
        checks.append(self._check_illegal_state_transition())
        checks.append(self._check_hypothesis_self_promotion())
        checks.append(self._check_audit_reconstruction_completeness())
        return IntegrityReport(checks=tuple(checks))

    def _prepared_request_events(self) -> tuple[Any, ...]:
        return tuple(
            event
            for event in self._audit
            if event.event_kind == "MODEL_REQUEST_PREPARED_OFFLINE"
        )

    def _check_future_leakage(self) -> IntegrityCheckResult:
        prepared = self._prepared_request_events()
        previous_decision: datetime | None = None
        for event in prepared:
            observation = event.payload["context"]["observation"]
            decision_time = _parse_dt(observation["decision_time"], "observation.decision_time")
            exchange_time = _parse_dt(observation["exchange_time"], "observation.exchange_time")
            if previous_decision is not None and decision_time < previous_decision:
                return IntegrityCheckResult(
                    "future_leakage", False,
                    f"observation decision_time regressed at request {event.request_id}",
                )
            previous_decision = decision_time
            if event.observation_identity != observation["observation_identity"]:
                return IntegrityCheckResult(
                    "future_leakage", False,
                    f"request {event.request_id} audit observation identity does not match context",
                )
            for bar in observation["bars"]:
                available_at = _parse_dt(bar["available_at"], "bar.available_at")
                close_time = _parse_dt(bar["close_time"], "bar.close_time")
                if available_at > decision_time:
                    return IntegrityCheckResult(
                        "future_leakage", False,
                        f"request {event.request_id} exposed future bar "
                        f"available_at {available_at.isoformat()} > decision_time "
                        f"{decision_time.isoformat()}",
                    )
                if close_time > exchange_time:
                    return IntegrityCheckResult(
                        "future_leakage", False,
                        f"request {event.request_id} exposed future bar close_time "
                        f"{close_time.isoformat()} > exchange_time {exchange_time.isoformat()}",
                    )
        return IntegrityCheckResult("future_leakage", True, f"{len(prepared)} requests causal")

    def _check_duplicate_missing_wake(self) -> IntegrityCheckResult:
        sessions = self._archive.session_identities()
        if not sessions:
            return IntegrityCheckResult(
                "duplicate_missing_wake", False, "wake ledger archive is empty"
            )
        seen_close: set[str] = set()
        for session in sessions:
            schedule = self._archive.schedule(session)
            wakes = self._archive.wakes(session)
            if len(wakes) != len(schedule):
                return IntegrityCheckResult(
                    "duplicate_missing_wake", False,
                    f"session {session} has {len(wakes)} wakes for {len(schedule)} scheduled 5m closes",
                )
            close_times = [wake.close_time for wake in wakes]
            if len({_iso_key(value) for value in close_times}) != len(close_times):
                return IntegrityCheckResult(
                    "duplicate_missing_wake", False,
                    f"session {session} contains a duplicate wake close_time",
                )
            if close_times != list(schedule):
                return IntegrityCheckResult(
                    "duplicate_missing_wake", False,
                    f"session {session} wake closes do not match the governed schedule",
                )
            for wake in wakes:
                key = _iso_key(wake.close_time)
                if key in seen_close:
                    return IntegrityCheckResult(
                        "duplicate_missing_wake", False,
                        f"wake close_time {key} repeated across sessions",
                    )
                seen_close.add(key)
        return IntegrityCheckResult(
            "duplicate_missing_wake", True,
            f"{len(sessions)} sessions, one wake per scheduled 5m close",
        )

    def _check_duplicate_missing_request(self) -> IntegrityCheckResult:
        bindings = self._archive.all_bindings()
        bound_request_ids = {binding.request_id for binding in bindings}
        wake_request_ids = set()
        for wake in self._archive.all_wakes():
            if wake.request_id is None:
                return IntegrityCheckResult(
                    "duplicate_missing_request", False,
                    f"governed wake {wake.wake_identity} has no admitted request",
                )
            wake_request_ids.add(wake.request_id)
        if bound_request_ids != wake_request_ids:
            return IntegrityCheckResult(
                "duplicate_missing_request", False,
                "wake request ids do not match ledger bindings",
            )
        prepared = self._prepared_request_events()
        prepared_ids = {event.request_id for event in prepared}
        if prepared_ids != bound_request_ids:
            missing = sorted(prepared_ids - bound_request_ids)
            orphan = sorted(bound_request_ids - prepared_ids)
            return IntegrityCheckResult(
                "duplicate_missing_request", False,
                f"prepared requests vs wake bindings mismatch; missing={missing}, orphan={orphan}",
            )
        for request_id in prepared_ids:
            raw = [
                event for event in self._audit
                if event.request_id == request_id and event.event_kind == "MODEL_RESPONSE_RAW"
            ]
            normalized = [
                event for event in self._audit
                if event.request_id == request_id
                and event.event_kind == "MODEL_RESPONSE_NORMALIZED"
            ]
            if len(raw) != 1 or len(normalized) != 1:
                return IntegrityCheckResult(
                    "duplicate_missing_request", False,
                    f"request {request_id} must have exactly one raw and one normalized response",
                )
            for binding in bindings:
                if binding.retry_count != 0:
                    return IntegrityCheckResult(
                        "duplicate_missing_request", False,
                        f"request {binding.request_id} carries non-zero retry count",
                    )
        return IntegrityCheckResult(
            "duplicate_missing_request", True,
            f"{len(prepared_ids)} requests, each bound to exactly one wake, retries zero",
        )

    def _check_identity_drift(self) -> IntegrityCheckResult:
        expected_trader = self._runtime.trader_identity.identity
        if self._result is not None and self._result.trader_identity != expected_trader:
            return IntegrityCheckResult(
                "identity_drift", False, "replay result trader identity drifted"
            )
        for event in self._audit:
            if event.trader_identity != expected_trader:
                return IntegrityCheckResult(
                    "identity_drift", False,
                    f"audit event {event.event_id} has a different trader identity",
                )
        for wake in self._archive.all_wakes():
            if wake.trader_identity != expected_trader:
                return IntegrityCheckResult(
                    "identity_drift", False,
                    f"wake {wake.wake_identity} has a different trader identity",
                )
        prepared = self._prepared_request_events()
        contract_identities = {
            event.payload["runtime_contract"]["identity"] for event in prepared
        }
        if len(contract_identities) != 1:
            return IntegrityCheckResult(
                "identity_drift", False,
                "runtime contract identity is not stable across prepared requests",
            )
        allowed_mappings = set(self._slice.mapping_identities)
        for event in prepared:
            observation = event.payload["context"]["observation"]
            if observation["product"] != self._slice.product:
                return IntegrityCheckResult(
                    "identity_drift", False,
                    f"request {event.request_id} observation product drifted",
                )
            if observation["concrete_contract"] != self._slice.concrete_contract:
                return IntegrityCheckResult(
                    "identity_drift", False,
                    f"request {event.request_id} observation concrete contract drifted",
                )
            if observation["mapping_identity"] not in allowed_mappings:
                return IntegrityCheckResult(
                    "identity_drift", False,
                    f"request {event.request_id} used an out-of-slice mapping identity",
                )
        return IntegrityCheckResult(
            "identity_drift", True,
            "single trader identity and stable runtime contract across all records",
        )

    def _check_clock_regression(self) -> IntegrityCheckResult:
        previous: datetime | None = None
        for event in self._audit:
            occurred = event.occurred_at
            if previous is not None and occurred < previous:
                return IntegrityCheckResult(
                    "clock_regression", False,
                    f"audit time regressed at sequence {event.sequence}",
                )
            previous = occurred
        per_request: dict[str, list[Any]] = {}
        for event in self._audit:
            if event.request_id:
                per_request.setdefault(event.request_id, []).append(event)
        for request_id, events in per_request.items():
            events_sorted = sorted(events, key=lambda item: item.sequence)
            for earlier, later in zip(events_sorted, events_sorted[1:]):
                if later.occurred_at < earlier.occurred_at:
                    return IntegrityCheckResult(
                        "clock_regression", False,
                        f"request {request_id} timeline regressed",
                    )
        return IntegrityCheckResult(
            "clock_regression", True,
            f"audit timeline monotonic across {len(self._audit)} events",
        )

    def _check_restart_continuity(self) -> IntegrityCheckResult:
        sealed = [
            event for event in self._audit if event.event_kind == "REPLAY_STATE_SEALED"
        ]
        verified = [
            event for event in self._audit if event.event_kind == "REPLAY_RESTART_VERIFIED"
        ]
        if not verified:
            if self._result is not None and self._result.r1_restart_verified:
                return IntegrityCheckResult(
                    "restart_continuity", False,
                    "R1 restart claimed verified but no verified restart event exists in audit",
                )
        else:
            for event in verified:
                if event.payload.get("restart_continuity") != "VERIFIED":
                    return IntegrityCheckResult(
                        "restart_continuity", False,
                        "a restart event did not record verified continuity",
                    )
            if len(sealed) < len(verified):
                return IntegrityCheckResult(
                    "restart_continuity", False,
                    "a verified restart has no preceding state seal",
                )
        if self._result is not None:
            current = ReplayStateSealer.compute_state_identity(
                runtime=self._runtime,
                slice_=self._slice,
                wake_archive_path=self._archive.path,
                exclude_event_kinds=REPLAY_CONTROL_EVENT_KINDS,
            )
            if current != self._result.state_identity:
                return IntegrityCheckResult(
                    "restart_continuity", False,
                    "final state identity is not reconstructable deterministically",
                )
        return IntegrityCheckResult(
            "restart_continuity", True,
            f"{len(sealed)} seals, {len(verified)} verified restarts, "
            "final state identity reconstructable",
        )

    def _check_memory_reset(self) -> IntegrityCheckResult:
        memory = self._runtime.store.load_working_memory()
        timestamps = [mutation.timestamp for mutation in memory.mutation_history]
        if any(
            later < earlier
            for earlier, later in zip(timestamps, timestamps[1:])
        ):
            return IntegrityCheckResult(
                "memory_reset", False, "working memory mutation timestamps regress"
            )
        mutation_audit = [
            event for event in self._audit
            if event.event_kind == "DS_WORKING_MEMORY_MUTATION"
        ]
        if len(mutation_audit) != len(timestamps):
            return IntegrityCheckResult(
                "memory_reset", False,
                f"working memory mutation history ({len(timestamps)}) does not match "
                f"audited mutations ({len(mutation_audit)})",
            )
        intent_events = [
            event for event in self._audit
            if event.event_kind == "REPLAY_INTENT_POSITION"
        ]
        if intent_events:
            last_intent = intent_events[-1]
            if memory.attention_mode.value != last_intent.payload["attention_mode_after"]:
                return IntegrityCheckResult(
                    "memory_reset", False,
                    "final attention mode does not match the last recorded decision state",
                )
        return IntegrityCheckResult(
            "memory_reset", True,
            f"memory has {len(timestamps)} monotonic mutations; no reset detected",
        )

    def _check_illegal_state_transition(self) -> IntegrityCheckResult:
        intent_events = [
            event for event in self._audit
            if event.event_kind == "REPLAY_INTENT_POSITION"
        ]
        if not intent_events:
            return IntegrityCheckResult(
                "illegal_state_transition", False, "no decision-state events recorded"
            )
        for event in intent_events:
            payload = event.payload
            before = AttentionMode(payload["attention_mode_before"])
            after = AttentionMode(payload["attention_mode_after"])
            try:
                decision = _decision_from_payload(
                    action=payload["action"],
                    direction=payload["direction"],
                    family=payload["family"],
                    attention_mode=payload["attention_mode_after"],
                )
                computed = validate_transition(before, decision)
            except ValueError as error:
                return IntegrityCheckResult(
                    "illegal_state_transition", False,
                    f"event {event.event_id} transition invalid: {error}",
                )
            if computed != after:
                return IntegrityCheckResult(
                    "illegal_state_transition", False,
                    f"event {event.event_id} transition {before.value}->{after.value} "
                    f"is not allowed by the frozen transition guard",
                )
            if not payload.get("execution_claim") is False or not payload.get("intent_only"):
                return IntegrityCheckResult(
                    "illegal_state_transition", False,
                    f"event {event.event_id} makes an execution claim in V0.1",
                )
        return IntegrityCheckResult(
            "illegal_state_transition", True,
            f"{len(intent_events)} decision-state events all legal and intent-only",
        )

    def _check_hypothesis_self_promotion(self) -> IntegrityCheckResult:
        hypotheses = self._runtime.store.list_hypotheses(limit=None)
        for hypothesis in hypotheses:
            if hypothesis.executable_policy or hypothesis.status not in HYPOTHESIS_STATUSES:
                return IntegrityCheckResult(
                    "hypothesis_self_promotion", False,
                    f"hypothesis {hypothesis.hypothesis_id} is policy or has invalid status",
                )
        exported = self._runtime.portable_export()
        for revision in exported.get("hypothesis_revisions", ()):
            after = revision.get("after_state", {})
            if after.get("executable_policy") is not False:
                return IntegrityCheckResult(
                    "hypothesis_self_promotion", False,
                    "a hypothesis revision promoted itself to executable policy",
                )
        for event in self._audit:
            if event.event_kind in FORBIDDEN_POLICY_WRITE_KINDS:
                return IntegrityCheckResult(
                    "hypothesis_self_promotion", False,
                    f"audit contains a forbidden policy/canon write event {event.event_kind}",
                )
        return IntegrityCheckResult(
            "hypothesis_self_promotion", True,
            "hypotheses remain non-executable; no policy or canon write recorded",
        )

    def _check_audit_reconstruction_completeness(self) -> IntegrityCheckResult:
        prepared = self._prepared_request_events()
        raw_count = len(
            [event for event in self._audit if event.event_kind == "MODEL_RESPONSE_RAW"]
        )
        normalized_count = len(
            [event for event in self._audit if event.event_kind == "MODEL_RESPONSE_NORMALIZED"]
        )
        intent_count = len(
            [event for event in self._audit if event.event_kind == "REPLAY_INTENT_POSITION"]
        )
        wake_count = len(self._archive.all_wakes())
        binding_count = len(self._archive.all_bindings())
        counts = {
            "prepared": len(prepared),
            "raw": raw_count,
            "normalized": normalized_count,
            "intent": intent_count,
            "wakes": wake_count,
            "bindings": binding_count,
        }
        if self._result is not None:
            counts["steps"] = self._result.step_count
            counts["result_wakes"] = self._result.wake_count
            counts["result_requests"] = self._result.request_count
        if len(set(counts.values())) != 1:
            return IntegrityCheckResult(
                "audit_reconstruction_completeness", False,
                f"reconstruction counts diverge: {counts}",
            )
        for event in self._audit:
            if event.event_kind == "REPLAY_INTENT_POSITION":
                payload = event.payload
                if not all(
                    payload.get(key)
                    for key in (
                        "observation_identity", "wake_identity", "request_id"
                    )
                ):
                    return IntegrityCheckResult(
                        "audit_reconstruction_completeness", False,
                        f"intent event {event.event_id} misses a required identity binding",
                    )
        return IntegrityCheckResult(
            "audit_reconstruction_completeness", True,
            f"all counts agree: {counts}",
        )


def _iso_key(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


__all__ = [
    "INTEGRITY_AUDITOR_VERSION",
    "IntegrityCheckResult",
    "IntegrityReport",
    "ReplayIntegrityAuditor",
]

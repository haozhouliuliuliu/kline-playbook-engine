"""Minimum deterministic validation connection semantics for Skeleton v1.0."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Iterable

from src.data_substrate import CompletedBar
from src.strategy_evidence import (
    DatasetClass,
    EvidenceLedger,
    EvidenceRecord,
    ExperimentIdentity,
    FinalUnseenFirewall,
    StrategyIdentity,
)


class ChronologyError(ValueError):
    pass


class ValidationMode(str, Enum):
    FAST = "FAST"
    CONFIRMATORY = "CONFIRMATORY"


class ValidationDisposition(str, Enum):
    REJECTED = "REJECTED"
    CONFIRMED = "CONFIRMED"


@dataclass(frozen=True)
class ValidationInput:
    request_id: str
    bar: CompletedBar
    decision_at: datetime

    def __post_init__(self) -> None:
        if not self.request_id:
            raise ValueError("validation request_id is required")
        if self.decision_at.tzinfo is None:
            raise ValueError("decision timestamp must be timezone-aware")


@dataclass(frozen=True)
class ExecutionEvent:
    timestamp: datetime
    event_type: str
    request_id: str


@dataclass(frozen=True)
class ValidationRunResult:
    allowed: bool
    events: tuple[ExecutionEvent, ...]
    access_record: EvidenceRecord
    validation_record: EvidenceRecord | None


class ChronologicalValidationRunner:
    """A neutral visible-input -> intent -> order -> fill feasibility runner."""

    _EVENT_ORDER = {
        "VISIBLE_MARKET_INPUT": 0,
        "STRATEGY_INTENT": 1,
        "ORDER_CREATED": 2,
        "FILL_ELIGIBLE": 3,
    }

    def __init__(self, ledger: EvidenceLedger, firewall: FinalUnseenFirewall) -> None:
        self._ledger = ledger
        self._firewall = firewall

    @staticmethod
    def _validate_binding(
        strategy: StrategyIdentity,
        experiment: ExperimentIdentity,
        artifact_identity_id: str,
        artifact_code_hash: str,
    ) -> None:
        if artifact_identity_id != strategy.identity_id or artifact_code_hash != strategy.code_hash:
            raise ValueError("strategy artifact does not match strategy identity")
        expected = ExperimentIdentity.from_strategy(
            strategy, experiment.data_version, experiment.dataset_exposure_reference
        )
        if expected != experiment:
            raise ValueError("experiment is not bound to the supplied strategy identity")

    @classmethod
    def _ordered_events(cls, inputs: Iterable[ValidationInput]) -> tuple[ExecutionEvent, ...]:
        ordered_inputs = tuple(inputs)
        previous_key: tuple[datetime, str] | None = None
        for item in ordered_inputs:
            if not item.bar.is_visible_at(item.decision_at):
                raise ChronologyError("strategy intent cannot use an unavailable completed bar")
            key = (item.decision_at, item.request_id)
            if previous_key is not None and key <= previous_key:
                raise ChronologyError("validation inputs must be strictly chronological by decision time and request_id")
            previous_key = key

        events: list[ExecutionEvent] = []
        for item in ordered_inputs:
            events.extend(
                (
                    ExecutionEvent(item.bar.available_at, "VISIBLE_MARKET_INPUT", item.request_id),
                    ExecutionEvent(item.decision_at, "STRATEGY_INTENT", item.request_id),
                    ExecutionEvent(item.decision_at, "ORDER_CREATED", item.request_id),
                    ExecutionEvent(item.decision_at, "FILL_ELIGIBLE", item.request_id),
                )
            )
        return tuple(sorted(events, key=lambda event: (event.timestamp, cls._EVENT_ORDER[event.event_type], event.request_id)))

    def run(
        self,
        *,
        mode: ValidationMode,
        strategy: StrategyIdentity,
        experiment: ExperimentIdentity,
        artifact_identity_id: str,
        artifact_code_hash: str,
        dataset_class: DatasetClass,
        inputs: Iterable[ValidationInput],
        disposition: ValidationDisposition | None = None,
    ) -> ValidationRunResult:
        self._validate_binding(strategy, experiment, artifact_identity_id, artifact_code_hash)
        if mode is ValidationMode.FAST and disposition is ValidationDisposition.CONFIRMED:
            raise ValueError("FAST mode cannot establish confirmatory validity")

        access = self._firewall.request_access(experiment, dataset_class)
        if not access.allowed:
            return ValidationRunResult(False, (), access.record, None)

        events = self._ordered_events(inputs)
        validation_record = None
        if disposition is ValidationDisposition.REJECTED:
            validation_record = self._ledger.append(
                EvidenceRecord("VALIDATION_REJECTED", experiment, dataset_class, "REJECTED")
            )
        elif disposition is ValidationDisposition.CONFIRMED:
            validation_record = self._ledger.append(
                EvidenceRecord("VALIDATION_CONFIRMED", experiment, dataset_class, "CONFIRMED")
            )
        return ValidationRunResult(True, events, access.record, validation_record)

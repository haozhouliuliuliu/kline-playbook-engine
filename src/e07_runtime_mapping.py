"""Runtime-facing E07 -> canonical eligibility resolution, fail closed."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json

from src.candidate_eligibility import CandidateEligibilityGate, CandidatePartitionReference, ConcreteContractMappingResult
from src.source_governed_mapping import SourceGovernedMappingSchedule


def _hash(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class RuntimeCandidateInputIdentity:
    strategy_identity: str
    e07_schedule_identity: str
    qualified_eligibility_view_identity: str
    canonical_parent_identity: str
    session_authority_identity: str
    machine_implementation_identity: str
    partition_identity: str

    def __post_init__(self) -> None:
        if not all(isinstance(item, str) and item.strip() for item in self.__dict__.values()):
            raise ValueError("runtime candidate input identity requires all bindings")

    @property
    def identity_id(self) -> str:
        return _hash(self.__dict__)


@dataclass(frozen=True)
class RuntimeCandidateInputResolution:
    partition: CandidatePartitionReference
    identity: RuntimeCandidateInputIdentity


class E07RuntimeMappingWiring:
    """Resolve a research symbol before canonical partition access.

    The caller supplies the partition identity selected by the governed canonical
    inventory.  This module never invents a roll, bar, partition, or fallback.
    """

    def __init__(self, schedule: SourceGovernedMappingSchedule, eligibility_gate: CandidateEligibilityGate, canonical_contracts: frozenset[str], *, strategy_identity: str, session_authority_identity: str, machine_implementation_identity: str) -> None:
        if not isinstance(schedule, SourceGovernedMappingSchedule) or not isinstance(eligibility_gate, CandidateEligibilityGate):
            raise ValueError("runtime mapping requires source schedule and eligibility gate")
        if not canonical_contracts:
            raise ValueError("runtime mapping requires canonical concrete contracts")
        if schedule.validate_canonical_membership(canonical_contracts):
            raise ValueError("E07 schedule has a target outside the canonical contract universe")
        if not all(isinstance(item, str) and item.strip() for item in (strategy_identity, session_authority_identity, machine_implementation_identity)):
            raise ValueError("runtime mapping identity bindings are required")
        self._schedule, self._gate, self._contracts = schedule, eligibility_gate, canonical_contracts
        self._strategy, self._session, self._machine = strategy_identity, session_authority_identity, machine_implementation_identity

    def resolve(self, *, research_symbol: str, decision_at: datetime, partition_identity: str) -> RuntimeCandidateInputResolution:
        mapped = self._schedule.resolve(research_symbol, decision_at)
        if mapped.concrete_instrument_id not in self._contracts:
            raise ValueError("E07_RUNTIME_CONTRACT_OUTSIDE_CANONICAL_UNIVERSE")
        partition = self._gate.require_mapping_eligible(
            ConcreteContractMappingResult(mapped.schedule_identity_id, mapped.concrete_instrument_id, decision_at.date()),
            partition_identity=partition_identity,
            parent_corpus_identity=self._gate.view.parent_corpus_identity,
        )
        identity = RuntimeCandidateInputIdentity(
            strategy_identity=self._strategy,
            e07_schedule_identity=mapped.schedule_identity_id,
            qualified_eligibility_view_identity=partition.qualified_eligibility_view_identity,
            canonical_parent_identity=partition.parent_corpus_identity,
            session_authority_identity=self._session,
            machine_implementation_identity=self._machine,
            partition_identity=partition.partition_identity,
        )
        return RuntimeCandidateInputResolution(partition, identity)

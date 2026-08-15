"""Strategy identity, factual evidence, and final-unseen access boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Any


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


class DatasetClass(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    VALIDATION = "VALIDATION"
    FINAL_UNSEEN = "FINAL_UNSEEN"


class LifecycleState(str, Enum):
    DRAFT = "DRAFT"
    CANDIDATE = "CANDIDATE"
    RETIRED = "RETIRED"


@dataclass(frozen=True)
class TypedParameter:
    name: str
    type_name: str
    value: str | int | float | bool

    def __post_init__(self) -> None:
        expected = {"str": str, "int": int, "float": float, "bool": bool}.get(self.type_name)
        if not self.name or expected is None or type(self.value) is not expected:
            raise ValueError("parameter name, declared type, and value must agree")

    def as_dict(self) -> dict[str, str | int | float | bool]:
        return {"name": self.name, "type": self.type_name, "value": self.value}


@dataclass(frozen=True)
class StrategyIdentity:
    research_lineage_id: str
    family_id: str
    strategy_version: str
    source: str
    applicable_instruments: tuple[str, ...]
    timeframe: str
    parameters: tuple[TypedParameter, ...]
    code_hash: str
    environment_hash: str
    required_feature_versions: tuple[str, ...]
    lifecycle_state: LifecycleState
    data_exposure_history_reference: str
    parent_identity_id: str | None = None

    def __post_init__(self) -> None:
        required = (
            self.research_lineage_id,
            self.family_id,
            self.strategy_version,
            self.source,
            self.timeframe,
            self.code_hash,
            self.environment_hash,
            self.data_exposure_history_reference,
        )
        if not all(required) or not self.applicable_instruments:
            raise ValueError("strategy identity has required empty fields")
        if tuple(sorted(set(self.applicable_instruments))) != self.applicable_instruments:
            raise ValueError("applicable instruments must be sorted and unique")
        names = tuple(parameter.name for parameter in self.parameters)
        if len(names) != len(set(names)):
            raise ValueError("parameter names must be unique")
        if tuple(sorted(set(self.required_feature_versions))) != self.required_feature_versions:
            raise ValueError("feature versions must be sorted and unique")

    @property
    def parameter_hash(self) -> str:
        return _canonical_hash([parameter.as_dict() for parameter in self.parameters])

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "research_lineage_id": self.research_lineage_id,
                "family_id": self.family_id,
                "strategy_version": self.strategy_version,
                "source": self.source,
                "applicable_instruments": self.applicable_instruments,
                "timeframe": self.timeframe,
                "parameters": [parameter.as_dict() for parameter in self.parameters],
                "code_hash": self.code_hash,
                "environment_hash": self.environment_hash,
                "required_feature_versions": self.required_feature_versions,
                "lifecycle_state": self.lifecycle_state.value,
                "data_exposure_history_reference": self.data_exposure_history_reference,
                "parent_identity_id": self.parent_identity_id,
            }
        )


class StrategyCatalog:
    """Append-only catalog; a family/version cannot silently change meaning."""

    def __init__(self) -> None:
        self._records: dict[str, StrategyIdentity] = {}
        self._version_keys: dict[tuple[str, str, str], str] = {}

    @property
    def records(self) -> tuple[StrategyIdentity, ...]:
        return tuple(self._records.values())

    def register(self, identity: StrategyIdentity) -> StrategyIdentity:
        existing = self._records.get(identity.identity_id)
        if existing is not None:
            return existing
        if identity.parent_identity_id is not None:
            parent = self._records.get(identity.parent_identity_id)
            if parent is None:
                raise ValueError("parent identity must already be registered")
            if parent.research_lineage_id != identity.research_lineage_id:
                raise ValueError("child identity must retain its research lineage")
        version_key = (identity.research_lineage_id, identity.family_id, identity.strategy_version)
        prior_id = self._version_keys.get(version_key)
        if prior_id is not None and prior_id != identity.identity_id:
            raise ValueError("a strategy family/version cannot be reused with different evidence")
        self._records[identity.identity_id] = identity
        self._version_keys[version_key] = identity.identity_id
        return identity


@dataclass(frozen=True)
class ExperimentIdentity:
    research_lineage_id: str
    strategy_identity_id: str
    family_id: str
    strategy_version: str
    code_hash: str
    parameter_hash: str
    environment_hash: str
    data_version: str
    feature_versions: tuple[str, ...]
    dataset_exposure_reference: str

    @classmethod
    def from_strategy(
        cls, strategy: StrategyIdentity, data_version: str, dataset_exposure_reference: str
    ) -> "ExperimentIdentity":
        if not data_version or not dataset_exposure_reference:
            raise ValueError("data version and exposure reference are required")
        return cls(
            strategy.research_lineage_id,
            strategy.identity_id,
            strategy.family_id,
            strategy.strategy_version,
            strategy.code_hash,
            strategy.parameter_hash,
            strategy.environment_hash,
            data_version,
            strategy.required_feature_versions,
            dataset_exposure_reference,
        )

    @property
    def experiment_id(self) -> str:
        return _canonical_hash(
            {
                "research_lineage_id": self.research_lineage_id,
                "strategy_identity_id": self.strategy_identity_id,
                "family_id": self.family_id,
                "strategy_version": self.strategy_version,
                "code_hash": self.code_hash,
                "parameter_hash": self.parameter_hash,
                "environment_hash": self.environment_hash,
                "data_version": self.data_version,
                "feature_versions": self.feature_versions,
                "dataset_exposure_reference": self.dataset_exposure_reference,
            }
        )

    def validate_strategy(self, strategy: StrategyIdentity) -> None:
        expected = (
            strategy.research_lineage_id,
            strategy.identity_id,
            strategy.family_id,
            strategy.strategy_version,
            strategy.code_hash,
            strategy.parameter_hash,
            strategy.environment_hash,
            strategy.required_feature_versions,
        )
        actual = (
            self.research_lineage_id,
            self.strategy_identity_id,
            self.family_id,
            self.strategy_version,
            self.code_hash,
            self.parameter_hash,
            self.environment_hash,
            self.feature_versions,
        )
        if actual != expected:
            raise ValueError("experiment identity does not bind the supplied strategy identity")


@dataclass(frozen=True)
class EvidenceRecord:
    event_type: str
    experiment: ExperimentIdentity
    dataset_class: DatasetClass
    outcome: str
    lifecycle_state: LifecycleState | None = None
    evidence_reference: str | None = None
    fact_reference: str | None = None

    def __post_init__(self) -> None:
        if not self.event_type or not self.outcome:
            raise ValueError("evidence event type and outcome are required")

    @property
    def record_id(self) -> str:
        identity = {
            "event_type": self.event_type,
            "experiment_id": self.experiment.experiment_id,
            "dataset_class": self.dataset_class.value,
            "outcome": self.outcome,
            "lifecycle_state": self.lifecycle_state.value if self.lifecycle_state else None,
            "evidence_reference": self.evidence_reference,
        }
        if self.fact_reference is not None:
            identity["fact_reference"] = self.fact_reference
        return _canonical_hash(identity)


class EvidenceLedger:
    """Append-only facts. It contains no mutable trading state or protected data."""

    def __init__(self) -> None:
        self._records: list[EvidenceRecord] = []
        self._record_ids: set[str] = set()

    @property
    def records(self) -> tuple[EvidenceRecord, ...]:
        return tuple(self._records)

    def append(self, record: EvidenceRecord) -> EvidenceRecord:
        if record.record_id in self._record_ids:
            raise ValueError("duplicate evidence record")
        self._records.append(record)
        self._record_ids.add(record.record_id)
        return record

    def exposures_for(self, research_lineage_id: str) -> tuple[DatasetClass, ...]:
        return tuple(
            record.dataset_class
            for record in self._records
            if record.experiment.research_lineage_id == research_lineage_id and record.outcome == "GRANTED"
        )


@dataclass(frozen=True)
class AccessResult:
    allowed: bool
    record: EvidenceRecord


class FinalUnseenFirewall:
    """Records access facts and denies final-unseen access until a future owner gate exists."""

    def __init__(self, ledger: EvidenceLedger) -> None:
        self._ledger = ledger

    def request_access(self, experiment: ExperimentIdentity, dataset_class: DatasetClass) -> AccessResult:
        if dataset_class is DatasetClass.FINAL_UNSEEN:
            record = EvidenceRecord("DATASET_ACCESS_DENIED", experiment, dataset_class, "DENIED")
            self._ledger.append(record)
            return AccessResult(False, record)
        record = EvidenceRecord("DATASET_ACCESS_GRANTED", experiment, dataset_class, "GRANTED")
        self._ledger.append(record)
        return AccessResult(True, record)

    def has_exposure(self, strategy: StrategyIdentity, dataset_class: DatasetClass) -> bool:
        return dataset_class in self._ledger.exposures_for(strategy.research_lineage_id)

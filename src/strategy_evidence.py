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
    # Legacy name kept for compatibility (existing code/tests still use it).
    FINAL_UNSEEN = "FINAL_UNSEEN"
    # Canonical frozen semantic name (Research Protocol v1.0 / 12-6-6 split).
    PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT = "PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT"
    SHADOW_FORWARD = "SHADOW_FORWARD"


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
    playbook_contract_identity: str | None = None

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
                "playbook_contract_identity": self.playbook_contract_identity,
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
    """Append-only facts. It contains no mutable trading state or protected data.

    Appending is idempotent by canonical ``record_id``: an exact re-append returns
    the already-stored canonical record without duplicating it, and repeated
    identical access/deny calls never crash or inflate the ledger. An impossible
    internal corruption (same record id mapping to non-equal content) still fails
    closed.
    """

    def __init__(self) -> None:
        self._records: list[EvidenceRecord] = []
        self._record_by_id: dict[str, EvidenceRecord] = {}

    @property
    def records(self) -> tuple[EvidenceRecord, ...]:
        return tuple(self._records)

    def append(self, record: EvidenceRecord) -> EvidenceRecord:
        record_id = record.record_id
        existing = self._record_by_id.get(record_id)
        if existing is not None:
            if existing == record:
                return existing
            raise ValueError("internal evidence corruption: record id maps to non-equal content")
        self._records.append(record)
        self._record_by_id[record_id] = record
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


@dataclass(frozen=True, init=False)
class ArtifactBinding:
    """Immutable artifact hash binding (P-06).

    ``sha256`` is always computed internally from the actual content bytes; there
    is no public constructor that accepts an arbitrary caller-supplied digest. Use
    ``from_bytes`` (or ``from_file``) as the only construction path. Identity
    covers kind/reference/sha256/byte_size/declared_version.
    """

    artifact_kind: str
    artifact_reference: str
    sha256: str
    byte_size: int
    declared_version: str | None = None

    @classmethod
    def from_bytes(
        cls,
        *,
        artifact_kind: str,
        artifact_reference: str,
        content: bytes,
        declared_version: str | None = None,
    ) -> "ArtifactBinding":
        if not isinstance(content, bytes):
            raise ValueError("artifact content must be bytes")
        # B-C01: the digest is computed ONLY here from the actual content bytes;
        # there is no caller-digest construction path. The frozen fields are
        # initialized with object.__setattr__.
        digest = sha256(content).hexdigest()
        obj = object.__new__(cls)
        object.__setattr__(obj, "artifact_kind", artifact_kind)
        object.__setattr__(obj, "artifact_reference", artifact_reference)
        object.__setattr__(obj, "sha256", digest)
        object.__setattr__(obj, "byte_size", len(content))
        object.__setattr__(obj, "declared_version", declared_version)
        obj.__post_init__()
        return obj

    @classmethod
    def from_file(
        cls,
        *,
        artifact_kind: str,
        artifact_reference: str,
        path: str,
        declared_version: str | None = None,
    ) -> "ArtifactBinding":
        with open(path, "rb") as handle:
            content = handle.read()
        return cls.from_bytes(
            artifact_kind=artifact_kind,
            artifact_reference=artifact_reference,
            content=content,
            declared_version=declared_version,
        )

    def __post_init__(self) -> None:
        if not self.artifact_kind or not self.artifact_reference:
            raise ValueError("artifact kind and reference are required")
        if type(self.sha256) is not str or len(self.sha256) != 64:
            raise ValueError("artifact sha256 must be a 64-character hex digest")
        if type(self.byte_size) is not int or self.byte_size < 0:
            raise ValueError("artifact byte size must be a non-negative integer")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "artifact_kind": self.artifact_kind,
                "artifact_reference": self.artifact_reference,
                "sha256": self.sha256,
                "byte_size": self.byte_size,
                "declared_version": self.declared_version,
            }
        )


@dataclass(frozen=True)
class OutcomeArtifactBindings:
    """Immutable container of the artifact bindings for one outcome test.

    ``feature_artifacts`` may be empty (a strategy with no separately versioned
    derived features). Registration verifies these artifacts against the strategy
    and experiment identity facts.
    """

    code_artifact: ArtifactBinding
    environment_artifact: ArtifactBinding
    data_artifact: ArtifactBinding
    feature_artifacts: tuple[ArtifactBinding, ...]

    def __post_init__(self) -> None:
        if self.code_artifact.artifact_kind != "code":
            raise ValueError("code artifact must use artifact_kind 'code'")
        if self.environment_artifact.artifact_kind != "environment":
            raise ValueError("environment artifact must use artifact_kind 'environment'")
        if self.data_artifact.artifact_kind != "data":
            raise ValueError("data artifact must use artifact_kind 'data'")
        if any(artifact.artifact_kind != "feature" for artifact in self.feature_artifacts):
            raise ValueError("feature artifacts must use artifact_kind 'feature'")
        versions = tuple(artifact.declared_version for artifact in self.feature_artifacts)
        if any(version is None for version in versions):
            raise ValueError("feature artifacts must declare a version")
        if tuple(sorted(set(versions))) != versions:
            raise ValueError("feature artifact versions must be sorted and unique")


class FinalUnseenFirewall:
    """Legacy compatibility firewall (deprecated for candidate outcomes).

    All pre-outcome research access rules are owned by
    `src.research_firewall.ResearchFirewall` — the single firewall owner. This class
    is a thin compatibility adapter that keeps the legacy `request_access` /
    `has_exposure` interface working for existing callers (validation_runner,
    portfolio_semantics, tests). Coarse DEVELOPMENT/VALIDATION grants here are NOT
    candidate-outcome authorization; candidate outcome-bearing access must pass the
    pre-outcome gate (`ResearchFirewall.request_candidate_outcome_access`).
    """

    def __init__(self, ledger: EvidenceLedger) -> None:
        from src.research_firewall import ResearchFirewall

        self._ledger = ledger
        self._owner = ResearchFirewall(ledger)

    def request_access(self, experiment: ExperimentIdentity, dataset_class: DatasetClass) -> AccessResult:
        return self._owner.legacy_request_access(experiment, dataset_class)

    def has_exposure(self, strategy: StrategyIdentity, dataset_class: DatasetClass) -> bool:
        return self._owner.has_exposure(strategy, dataset_class)

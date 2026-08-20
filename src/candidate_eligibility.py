"""Fail-closed candidate input eligibility over the accepted canonical corpus.

This module deliberately contains only partition identities and governed
metadata.  It never reads market values, changes the accepted corpus, or
authorizes candidate outcome access.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, Protocol

from src.canonical_identity import canonical_hash


VIEW_SCHEMA_VERSION = "canonical-qualified-eligibility-view-v1"
VIEW_VERSION = "QUALIFIED_ELIGIBILITY_VIEW_V1"
EXCLUSION_RULE = "UNIFORM_GOVERNED_FIRST_TRADING_DAY_EXCLUSION"
UNRESOLVED_FAIL_CLOSED = "UNRESOLVED_FAIL_CLOSED"


class CandidateEligibilityError(ValueError):
    """A machine-readable, fail-closed candidate input denial."""


def _required(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")


@dataclass(frozen=True, order=True)
class EligibilityPartition:
    """Identity-only description of one accepted canonical partition."""

    partition_identity: str
    concrete_contract: str
    trading_day: date

    def __post_init__(self) -> None:
        _required(self.partition_identity, "partition identity")
        _required(self.concrete_contract, "concrete contract")
        if not isinstance(self.trading_day, date):
            raise ValueError("trading day must be a date")

    def to_dict(self) -> dict[str, str]:
        return {
            "partition_identity": self.partition_identity,
            "concrete_contract": self.concrete_contract,
            "trading_day": self.trading_day.isoformat(),
        }


@dataclass(frozen=True)
class QualifiedEligibilityView:
    """Immutable identity-bound subset allowed as candidate-quality input."""

    parent_corpus_identity: str
    parent_manifest_identity: str
    contract_universe_identity: str
    contract_universe_source_artifact_sha256: str
    revalidation_evidence_identity: str
    authority_decision_evidence_identity: str
    implementation_identity: str
    excluded_partitions: tuple[EligibilityPartition, ...]
    included_partition_root_identity: str
    excluded_partition_count: int
    eligible_partition_count: int
    excluded_row_count: int
    no_candidate_outcome_used: bool = True
    schema_version: str = VIEW_SCHEMA_VERSION
    view_version: str = VIEW_VERSION
    exclusion_rule: str = EXCLUSION_RULE

    def __post_init__(self) -> None:
        for value, name in (
            (self.parent_corpus_identity, "parent corpus identity"),
            (self.parent_manifest_identity, "parent manifest identity"),
            (self.contract_universe_identity, "contract universe identity"),
            (self.contract_universe_source_artifact_sha256, "contract universe source artifact SHA256"),
            (self.revalidation_evidence_identity, "revalidation evidence identity"),
            (self.authority_decision_evidence_identity, "authority decision evidence identity"),
            (self.implementation_identity, "implementation identity"),
            (self.included_partition_root_identity, "included partition root identity"),
        ):
            _required(value, name)
        if self.schema_version != VIEW_SCHEMA_VERSION or self.view_version != VIEW_VERSION:
            raise ValueError("unsupported qualified eligibility view version")
        if self.exclusion_rule != EXCLUSION_RULE:
            raise ValueError("qualified eligibility view exclusion rule is not governed")
        if not self.no_candidate_outcome_used:
            raise ValueError("qualified eligibility view cannot bind candidate outcomes")
        ordered = tuple(sorted(self.excluded_partitions))
        if ordered != self.excluded_partitions or len({item.partition_identity for item in ordered}) != len(ordered):
            raise ValueError("excluded partitions must be unique and deterministically ordered")
        if self.excluded_partition_count != len(ordered) or self.eligible_partition_count < 0:
            raise ValueError("qualified eligibility view partition counts are inconsistent")
        if self.excluded_row_count < 0:
            raise ValueError("excluded row count must be non-negative")

    @property
    def excluded_partition_identities(self) -> tuple[str, ...]:
        return tuple(item.partition_identity for item in self.excluded_partitions)

    def identity(self) -> str:
        return canonical_hash(self.to_dict(include_identity=False))

    def to_dict(self, *, include_identity: bool = True) -> dict[str, object]:
        data: dict[str, object] = {
            "schema_version": self.schema_version,
            "view_version": self.view_version,
            "parent_corpus_identity": self.parent_corpus_identity,
            "parent_manifest_identity": self.parent_manifest_identity,
            "contract_universe_identity": self.contract_universe_identity,
            "contract_universe_source_artifact_sha256": self.contract_universe_source_artifact_sha256,
            "revalidation_evidence_identity": self.revalidation_evidence_identity,
            "authority_decision_evidence_identity": self.authority_decision_evidence_identity,
            "implementation_identity": self.implementation_identity,
            "exclusion_rule": self.exclusion_rule,
            "excluded_partitions": [item.to_dict() for item in self.excluded_partitions],
            "included_partition_root_identity": self.included_partition_root_identity,
            "excluded_partition_count": self.excluded_partition_count,
            "eligible_partition_count": self.eligible_partition_count,
            "excluded_row_count": self.excluded_row_count,
            "no_candidate_outcome_used": self.no_candidate_outcome_used,
        }
        if include_identity:
            data["qualified_eligibility_view_identity"] = self.identity()
        return data


@dataclass(frozen=True)
class CandidatePartitionReference:
    """The only successful result of candidate partition eligibility access."""

    partition_identity: str
    concrete_contract: str
    trading_day: date
    parent_corpus_identity: str
    qualified_eligibility_view_identity: str


class CandidateEligibilityGate:
    """Resolve candidate input by identity, denying unknown and excluded input."""

    def __init__(self, view: QualifiedEligibilityView, partitions: Iterable[EligibilityPartition]) -> None:
        self._view = view
        ordered = tuple(sorted(partitions))
        if not ordered or len({item.partition_identity for item in ordered}) != len(ordered):
            raise ValueError("candidate gate requires unique accepted partition identities")
        self._partitions = {item.partition_identity: item for item in ordered}
        excluded = set(view.excluded_partition_identities)
        if not excluded <= set(self._partitions):
            raise ValueError("view excludes a partition absent from the accepted inventory")
        eligible = tuple(sorted(set(self._partitions) - excluded))
        if len(eligible) != view.eligible_partition_count:
            raise ValueError("candidate gate eligible partition count conflicts with view")
        if canonical_hash(list(eligible)) != view.included_partition_root_identity:
            raise ValueError("candidate gate accepted inventory conflicts with view root")

    @property
    def view(self) -> QualifiedEligibilityView:
        return self._view

    def require_eligible(
        self,
        *,
        concrete_contract: str,
        trading_day: date,
        partition_identity: str,
        parent_corpus_identity: str,
    ) -> CandidatePartitionReference:
        if parent_corpus_identity != self._view.parent_corpus_identity:
            raise CandidateEligibilityError("CANDIDATE_CANONICAL_PARENT_IDENTITY_MISMATCH")
        partition = self._partitions.get(partition_identity)
        if partition is None:
            raise CandidateEligibilityError("CANDIDATE_PARTITION_UNKNOWN_IDENTITY")
        if partition.concrete_contract != concrete_contract or partition.trading_day != trading_day:
            raise CandidateEligibilityError("CANDIDATE_PARTITION_IDENTITY_MISMATCH")
        if partition_identity in self._view.excluded_partition_identities:
            raise CandidateEligibilityError("CANDIDATE_PARTITION_NOT_ELIGIBLE_FIRST_TRADING_DAY")
        return CandidatePartitionReference(
            partition_identity=partition.partition_identity,
            concrete_contract=partition.concrete_contract,
            trading_day=partition.trading_day,
            parent_corpus_identity=self._view.parent_corpus_identity,
            qualified_eligibility_view_identity=self._view.identity(),
        )

    def require_mapping_eligible(
        self,
        mapping: "ConcreteContractMappingResult",
        *,
        partition_identity: str,
        parent_corpus_identity: str,
    ) -> CandidatePartitionReference:
        if mapping.mapping_authority_identity == UNRESOLVED_FAIL_CLOSED:
            raise CandidateEligibilityError("CANDIDATE_MAPPING_AUTHORITY_UNRESOLVED_FAIL_CLOSED")
        return self.require_eligible(
            concrete_contract=mapping.concrete_contract,
            trading_day=mapping.trading_day,
            partition_identity=partition_identity,
            parent_corpus_identity=parent_corpus_identity,
        )


@dataclass(frozen=True)
class ConcreteContractMappingResult:
    """Minimal E07 seam: a mapping must resolve before eligibility is checked."""

    mapping_authority_identity: str
    concrete_contract: str
    trading_day: date

    def __post_init__(self) -> None:
        _required(self.mapping_authority_identity, "mapping authority identity")
        _required(self.concrete_contract, "concrete contract")


@dataclass(frozen=True)
class CandidateQualityDataIdentity:
    """Candidate-quality data lineage, intentionally not outcome-ready yet."""

    parent_corpus_identity: str
    qualified_eligibility_view_identity: str
    mapping_authority_identity: str
    price_limit_authority_identity: str
    other_governed_input_identities: tuple[str, ...]

    def __post_init__(self) -> None:
        for value, name in (
            (self.parent_corpus_identity, "parent corpus identity"),
            (self.qualified_eligibility_view_identity, "qualified view identity"),
            (self.mapping_authority_identity, "mapping authority identity"),
            (self.price_limit_authority_identity, "price-limit authority identity"),
        ):
            _required(value, name)
        if not self.other_governed_input_identities or any(not item for item in self.other_governed_input_identities):
            raise ValueError("candidate data identity requires governed input identities")

    @property
    def ready_for_candidate_outcome(self) -> bool:
        return (
            self.mapping_authority_identity != UNRESOLVED_FAIL_CLOSED
            and self.price_limit_authority_identity != UNRESOLVED_FAIL_CLOSED
        )

    def identity(self) -> str:
        return canonical_hash({
            "parent_corpus_identity": self.parent_corpus_identity,
            "qualified_eligibility_view_identity": self.qualified_eligibility_view_identity,
            "mapping_authority_identity": self.mapping_authority_identity,
            "price_limit_authority_identity": self.price_limit_authority_identity,
            "other_governed_input_identities": sorted(self.other_governed_input_identities),
        })


class _FirewallCandidateInputAuthorizer(Protocol):
    def require_candidate_canonical_input(self, **kwargs: object) -> CandidatePartitionReference: ...


class CandidateCanonicalInputGateway:
    """Candidate input caller that cannot access a partition except through the firewall."""

    def __init__(self, firewall: _FirewallCandidateInputAuthorizer, gate: CandidateEligibilityGate) -> None:
        self._firewall = firewall
        self._gate = gate

    def request_partition(
        self,
        *,
        concrete_contract: str,
        trading_day: date,
        partition_identity: str,
        parent_corpus_identity: str,
    ) -> CandidatePartitionReference:
        return self._firewall.require_candidate_canonical_input(
            eligibility_gate=self._gate,
            concrete_contract=concrete_contract,
            trading_day=trading_day,
            partition_identity=partition_identity,
            parent_corpus_identity=parent_corpus_identity,
        )

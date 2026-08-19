"""Generic deterministic Playbook Contract core (source-faithful research layer).

Lane B of the 2026-08-19 parallel work package. This module is deliberately
generic: it can represent ANY future human-source playbook and is independent of
whether any specific candidate family (for example the Raschke NR7 family) ever
passes semantic completion.

It implements the smallest deterministic transition:

    SOURCE CLAIM
    != PROJECT INTERPRETATION
    != MACHINE OPERATIONALIZATION

and connects source-faithful research semantics to the already-existing Strategy
Catalog machinery (`src.strategy_evidence.py`) through an explicit, fail-closed
bridge. Frozen authority (do not modify):

- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`

Hard boundaries (guaranteed by this module):

- No function here grants candidate outcome access.
  `src.research_firewall.ResearchFirewall` remains the sole outcome-access owner
  and this module deliberately does not import it.
- The bridge never automatically registers or authorizes a strategy merely
  because a playbook draft exists; registration into a `StrategyCatalog` is an
  explicit caller action.
- Validation is fail-closed: missing source references, missing interpretation
  provenance, unresolved critical ambiguity, a non-observable required input,
  silently collapsed source variants, a missing or duplicated PRIMARY, missing
  machine identities, missing instrument/timeframe scope, and an INFERRED
  transfer mislabeled EXPLICIT all mark the contract `NOT_MACHINE_READY`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Any

from src.strategy_evidence import (
    LifecycleState,
    StrategyIdentity,
    TypedParameter,
)


def canonical_hash(value: Any) -> str:
    """Deterministic canonical JSON+sha256 hash (same scheme as the project)."""
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


class ClaimStatus(str, Enum):
    """Provenance-of-meaning label of a source claim (Claim Schema v1.0)."""

    EXPLICIT = "EXPLICIT"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"


class TransferStatus(str, Enum):
    """How a source claim was transferred into a project interpretation."""

    EXPLICIT = "EXPLICIT"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"


class AmbiguityStatus(str, Enum):
    """Contract-level ambiguity state (Protocol v1.0 section 2)."""

    NONE = "NONE"
    RESOLVED = "RESOLVED"
    UNRESOLVED_CRITICAL = "UNRESOLVED_CRITICAL"


class ObservabilityStatus(str, Enum):
    """Point-in-time observability of a required observation surface."""

    OBSERVABLE_NOW = "OBSERVABLE_NOW"
    PARTIALLY_OBSERVABLE = "PARTIALLY_OBSERVABLE"
    NOT_OBSERVABLE_WITH_CURRENT_DATA = "NOT_OBSERVABLE_WITH_CURRENT_DATA"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class MachineReadiness(str, Enum):
    """Fail-closed readiness of a playbook contract for machine operationalization."""

    MACHINE_READY = "MACHINE_READY"
    NOT_MACHINE_READY = "NOT_MACHINE_READY"


def _require_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")


def _canonical_tuple(values: tuple[str, ...], name: str) -> tuple[str, ...]:
    """Set-like string collections must be sorted and unique when non-empty."""
    if not values:
        return values
    if tuple(sorted(set(values))) != values:
        raise ValueError(f"{name} must be sorted and unique")
    return values


@dataclass(frozen=True)
class SourceClaimRef:
    """A source-faithful claim reference (SOURCE layer, Claim Schema v1.0)."""

    claim_id: str
    source_id: str
    source_anchor: str
    claim_status: ClaimStatus

    def __post_init__(self) -> None:
        _require_text(self.claim_id, "claim id")
        _require_text(self.source_id, "source id")
        _require_text(self.source_anchor, "source anchor")
        if not isinstance(self.claim_status, ClaimStatus):
            raise ValueError("claim status must be a ClaimStatus")

    @property
    def claim_identity(self) -> str:
        return canonical_hash(
            {
                "claim_id": self.claim_id,
                "source_id": self.source_id,
                "source_anchor": self.source_anchor,
                "claim_status": self.claim_status.value,
            }
        )


@dataclass(frozen=True)
class ObservationSurface:
    """A required observation surface and its point-in-time observability."""

    surface_id: str
    required: bool
    observability_status: ObservabilityStatus
    missing_inputs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_text(self.surface_id, "observation surface id")
        if not isinstance(self.observability_status, ObservabilityStatus):
            raise ValueError("observability status must be an ObservabilityStatus")
        _canonical_tuple(self.missing_inputs, "missing inputs")

    @property
    def surface_identity(self) -> str:
        return canonical_hash(
            {
                "surface_id": self.surface_id,
                "required": self.required,
                "observability_status": self.observability_status.value,
                "missing_inputs": self.missing_inputs,
            }
        )


@dataclass(frozen=True)
class InterpretationBranch:
    """A project/AI interpretation grounded in source claims (INTERPRETATION layer)."""

    branch_id: str
    source_claim_ids: tuple[str, ...]
    source_basis: str
    transfer_status: TransferStatus
    primary_selected: bool = False
    variant_label: str | None = None
    interpretation_note: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.branch_id, "interpretation branch id")
        if not self.source_claim_ids:
            raise ValueError("an interpretation branch must reference at least one source claim")
        if not isinstance(self.transfer_status, TransferStatus):
            raise ValueError("transfer status must be a TransferStatus")

    @property
    def branch_identity(self) -> str:
        return canonical_hash(
            {
                "branch_id": self.branch_id,
                "source_claim_ids": tuple(sorted(set(self.source_claim_ids))),
                "source_basis": self.source_basis,
                "transfer_status": self.transfer_status.value,
                "primary_selected": self.primary_selected,
                "variant_label": self.variant_label,
                "interpretation_note": self.interpretation_note,
            }
        )


@dataclass(frozen=True)
class MachineOperationalization:
    """Machine operationalization reference (MACHINE layer).

    Holds the identity facts required by `StrategyIdentity`: implementation
    reference, code hash, environment hash, required feature versions and
    declared parameter identities. Empty `required_feature_versions` and
    `parameter_identities` are legitimate (zero-parameter fixed-rule strategies,
    or strategies with no separately versioned derived features); the mandatory
    scalar identity fields (`operationalization_reference`, `code_hash`,
    `environment_hash`) must still be present for machine readiness.
    """

    operationalization_reference: str
    code_hash: str
    environment_hash: str
    required_feature_versions: tuple[str, ...]
    parameter_identities: tuple[str, ...]

    def __post_init__(self) -> None:
        _canonical_tuple(self.required_feature_versions, "required feature versions")
        _canonical_tuple(self.parameter_identities, "parameter identities")

    @property
    def machine_identity(self) -> str:
        return canonical_hash(
            {
                "operationalization_reference": self.operationalization_reference,
                "code_hash": self.code_hash,
                "environment_hash": self.environment_hash,
                "required_feature_versions": self.required_feature_versions,
                "parameter_identities": self.parameter_identities,
            }
        )


@dataclass(frozen=True)
class PlaybookContract:
    """Generic deterministic Playbook Contract core representation.

    Holds the three mandatory layers separately (SOURCE CLAIM != PROJECT
    INTERPRETATION != MACHINE OPERATIONALIZATION), plus contract-level version,
    lineage, scope, ambiguity, observability and transfer facts. Construction is
    permissive for draft content; `validate_contract` is the fail-closed authority
    that marks `NOT_MACHINE_READY` until every requirement is satisfied.
    """

    schema_version: str
    contract_version: str
    contract_id: str
    research_lineage_id: str
    family_id: str
    source_claims: tuple[SourceClaimRef, ...] = ()
    source_bundle_identity: str = ""
    source_bundle_hash: str = ""
    source_only_session_identity: str = ""
    source_scope: str = ""
    interpretations: tuple[InterpretationBranch, ...] = ()
    ambiguity_status: AmbiguityStatus = AmbiguityStatus.NONE
    ambiguity_notes: str | None = None
    primary_required: bool = True
    source_variant_count: int = 1
    observation_surfaces: tuple[ObservationSurface, ...] = ()
    unavailable_inputs: tuple[str, ...] = ()
    instrument_scope: tuple[str, ...] = ()
    timeframe_scope: tuple[str, ...] = ()
    project_transfer_status: TransferStatus = TransferStatus.UNKNOWN
    machine: MachineOperationalization | None = None
    data_exposure_history_reference: str = ""
    parent_contract_id: str | None = None
    created_at: str = ""

    def __post_init__(self) -> None:
        _require_text(self.schema_version, "schema version")
        _require_text(self.contract_version, "contract version")
        _require_text(self.contract_id, "contract id")
        _require_text(self.research_lineage_id, "research lineage id")
        _require_text(self.family_id, "family id")
        if not isinstance(self.ambiguity_status, AmbiguityStatus):
            raise ValueError("ambiguity status must be an AmbiguityStatus")
        if not isinstance(self.project_transfer_status, TransferStatus):
            raise ValueError("project transfer status must be a TransferStatus")
        if self.source_variant_count < 1:
            raise ValueError("source variant count must be at least 1")
        _canonical_tuple(self.unavailable_inputs, "unavailable inputs")
        _canonical_tuple(self.instrument_scope, "instrument scope")
        _canonical_tuple(self.timeframe_scope, "timeframe scope")

    @property
    def contract_identity(self) -> str:
        return canonical_hash(
            {
                "schema_version": self.schema_version,
                "contract_version": self.contract_version,
                "contract_id": self.contract_id,
                "research_lineage_id": self.research_lineage_id,
                "family_id": self.family_id,
                "parent_contract_id": self.parent_contract_id,
                "source_claims": tuple(
                    sorted(claim.claim_identity for claim in self.source_claims)
                ),
                "source_bundle_identity": self.source_bundle_identity,
                "source_bundle_hash": self.source_bundle_hash,
                "source_only_session_identity": self.source_only_session_identity,
                "source_scope": self.source_scope,
                "interpretations": tuple(
                    sorted(branch.branch_identity for branch in self.interpretations)
                ),
                "ambiguity_status": self.ambiguity_status.value,
                "ambiguity_notes": self.ambiguity_notes,
                "primary_required": self.primary_required,
                "source_variant_count": self.source_variant_count,
                "observation_surfaces": tuple(
                    sorted(surface.surface_identity for surface in self.observation_surfaces)
                ),
                "unavailable_inputs": self.unavailable_inputs,
                "instrument_scope": self.instrument_scope,
                "timeframe_scope": self.timeframe_scope,
                "project_transfer_status": self.project_transfer_status.value,
                "machine": None if self.machine is None else self.machine.machine_identity,
                "data_exposure_history_reference": self.data_exposure_history_reference,
                "created_at": self.created_at,
            }
        )

    def machine_readiness(self) -> "ContractValidationResult":
        return validate_contract(self)

    def to_dict(self) -> dict[str, Any]:
        result = self.machine_readiness()
        return {
            "schema_version": self.schema_version,
            "contract_version": self.contract_version,
            "contract_id": self.contract_id,
            "contract_identity": self.contract_identity,
            "research_lineage_id": self.research_lineage_id,
            "family_id": self.family_id,
            "parent_contract_id": self.parent_contract_id,
            "machine_readiness": result.readiness.value,
            "machine_readiness_blockers": list(result.blockers),
        }


@dataclass(frozen=True)
class ContractValidationResult:
    """Fail-closed validation outcome for a playbook contract."""

    readiness: MachineReadiness
    blockers: tuple[str, ...]

    @property
    def ready(self) -> bool:
        return self.readiness is MachineReadiness.MACHINE_READY


def _collect_blockers(contract: PlaybookContract) -> tuple[str, ...]:
    """Deterministic fail-closed blocker collection. Empty means machine-ready."""
    blockers: list[str] = []

    # 1. Source references must be present (SOURCE layer).
    source_missing = not contract.source_claims or any(
        not claim.claim_id or not claim.source_id or not claim.source_anchor
        for claim in contract.source_claims
    )
    if source_missing or not (
        contract.source_bundle_identity
        and contract.source_bundle_hash
        and contract.source_only_session_identity
    ):
        blockers.append("SOURCE_REFERENCES_MISSING")

    # 2. Interpretation provenance must be present and resolvable (INTERPRETATION layer).
    claim_ids = {claim.claim_id for claim in contract.source_claims}
    if not contract.interpretations:
        blockers.append("INTERPRETATION_PROVENANCE_MISSING")
    else:
        if any(not branch.source_basis for branch in contract.interpretations):
            blockers.append("INTERPRETATION_PROVENANCE_MISSING")
        if any(
            not set(branch.source_claim_ids) <= claim_ids
            for branch in contract.interpretations
        ):
            blockers.append("INTERPRETATION_REFERENCES_UNKNOWN_SOURCE_CLAIM")

    # 3. Unresolved critical ambiguity stops instead of mining alternatives.
    if contract.ambiguity_status is AmbiguityStatus.UNRESOLVED_CRITICAL:
        blockers.append("UNRESOLVED_CRITICAL_AMBIGUITY")

    # 4. Required inputs must be observable point-in-time.
    required_surfaces = [surface for surface in contract.observation_surfaces if surface.required]
    if any(
        surface.observability_status
        in (
            ObservabilityStatus.NOT_OBSERVABLE_WITH_CURRENT_DATA,
            ObservabilityStatus.UNKNOWN,
        )
        for surface in required_surfaces
    ):
        blockers.append("REQUIRED_INPUT_NOT_OBSERVABLE")
    if {surface.surface_id for surface in required_surfaces} & set(contract.unavailable_inputs):
        blockers.append("REQUIRED_INPUT_NOT_OBSERVABLE")

    # 5. Multiple source-permitted variants cannot silently collapse.
    if contract.source_variant_count < 1:
        blockers.append("SOURCE_VARIANT_COUNT_INVALID")
    elif contract.source_variant_count > 1:
        labels = {branch.variant_label for branch in contract.interpretations}
        if None in labels or len(labels) < contract.source_variant_count:
            blockers.append("SOURCE_VARIANTS_SILENTLY_COLLAPSED")
        elif len(labels) > contract.source_variant_count:
            blockers.append("SOURCE_VARIANTS_INVENTED")
    else:
        labels = {branch.variant_label for branch in contract.interpretations}
        if len(labels) > 1:
            blockers.append("SOURCE_VARIANTS_INVENTED")

    # 6. Exactly one explicit PRIMARY where one is required.
    primary_count = sum(1 for branch in contract.interpretations if branch.primary_selected)
    if primary_count > 1:
        blockers.append("MULTIPLE_PRIMARY_SELECTED")
    if contract.primary_required and primary_count == 0:
        blockers.append("PRIMARY_MISSING")

    # 7. Machine identities required for StrategyIdentity must be present.
    # Empty `parameter_identities` / `required_feature_versions` are legitimate
    # values (zero-parameter fixed-rule strategies, or strategies with no
    # separately versioned derived features), not missing identity. Only the
    # mandatory scalar machine identity facts are required here.
    machine = contract.machine
    if machine is None:
        blockers.append("MACHINE_OPERATIONALIZATION_MISSING")
    elif not (
        machine.operationalization_reference
        and machine.code_hash
        and machine.environment_hash
    ):
        blockers.append("MACHINE_IDENTITIES_MISSING")

    # 8. Instrument and timeframe scope must be declared.
    if not contract.instrument_scope or not contract.timeframe_scope:
        blockers.append("SCOPE_MISSING")

    # 9. An INFERRED transfer must not be mislabeled EXPLICIT.
    if contract.project_transfer_status is TransferStatus.EXPLICIT:
        if any(
            branch.transfer_status in (TransferStatus.INFERRED, TransferStatus.UNKNOWN)
            for branch in contract.interpretations
        ):
            blockers.append("INFERRED_TRANSFER_MISLABELED_EXPLICIT")

    return tuple(dict.fromkeys(blockers))


def validate_contract(contract: PlaybookContract) -> ContractValidationResult:
    """Fail-closed validation: mark NOT_MACHINE_READY with deterministic blockers."""
    blockers = _collect_blockers(contract)
    if blockers:
        return ContractValidationResult(MachineReadiness.NOT_MACHINE_READY, blockers)
    return ContractValidationResult(MachineReadiness.MACHINE_READY, ())


def parameter_identity(parameter: TypedParameter) -> str:
    """Canonical identity of a typed parameter (matches the machine-layer declaration)."""
    return canonical_hash(parameter.as_dict())


def bridge_to_strategy_identity(
    contract: PlaybookContract,
    *,
    parameters: tuple[TypedParameter, ...],
    code_hash: str,
    environment_hash: str,
    required_feature_versions: tuple[str, ...],
    data_exposure_history_reference: str,
    lifecycle_state: LifecycleState = LifecycleState.DRAFT,
) -> StrategyIdentity:
    """Deterministic bridge to the existing StrategyIdentity model.

    Fail-closed rules:
    - the contract must already validate as MACHINE_READY (a draft never bridges);
    - every supplied machine input must match the contract's machine layer;
    - the caller-supplied parameters must match the declared parameter identities
      exactly. Empty `parameters` and/or `required_feature_versions` are
      legitimate exact matches (zero-parameter fixed-rule strategies, or
      strategies with no separately versioned derived features); a non-empty vs
      empty mismatch still fails closed.

    This function never registers into a StrategyCatalog and never grants any
    candidate outcome access. Registration/authorization remain explicit caller
    actions, and ResearchFirewall remains the sole outcome-access owner.
    """
    result = validate_contract(contract)
    if not result.ready:
        raise ValueError(
            "playbook contract is not machine ready: " + ",".join(result.blockers)
        )
    machine = contract.machine
    if machine is None:
        raise ValueError("playbook contract has no machine operationalization")
    if machine.code_hash != code_hash:
        raise ValueError("code hash does not match the contract machine layer")
    if machine.environment_hash != environment_hash:
        raise ValueError("environment hash does not match the contract machine layer")
    canonical_features = tuple(sorted(set(required_feature_versions)))
    if machine.required_feature_versions != canonical_features:
        raise ValueError("required feature versions do not match the contract machine layer")
    caller_parameter_ids = tuple(sorted({parameter_identity(p) for p in parameters}))
    if caller_parameter_ids != machine.parameter_identities:
        raise ValueError("parameters do not match the contract parameter identities")
    if data_exposure_history_reference != contract.data_exposure_history_reference:
        raise ValueError("data exposure reference does not match the contract")
    return StrategyIdentity(
        research_lineage_id=contract.research_lineage_id,
        family_id=contract.family_id,
        strategy_version=f"pc-{contract.contract_version}-{contract.contract_identity}",
        source=contract.source_scope or contract.family_id,
        applicable_instruments=tuple(sorted(set(contract.instrument_scope))),
        timeframe=",".join(sorted(contract.timeframe_scope)),
        parameters=parameters,
        code_hash=code_hash,
        environment_hash=environment_hash,
        required_feature_versions=canonical_features,
        lifecycle_state=lifecycle_state,
        data_exposure_history_reference=data_exposure_history_reference,
    )

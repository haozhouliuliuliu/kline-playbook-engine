"""Build the source-faithful Holy Grail V0.2 Playbook Contract draft.

This builder preserves SOURCE CLAIM, PROJECT INTERPRETATION, and MACHINE
OPERATIONALIZATION as separate layers.  It deliberately leaves every FGH
semantic gate unresolved and never creates a StrategyIdentity or registers an
outcome test.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.playbook_contract import (
    AmbiguityStatus,
    ClaimStatus,
    InterpretationBranch,
    ObservationSurface,
    ObservabilityStatus,
    PlaybookContract,
    SourceClaimRef,
    TransferStatus,
    validate_contract,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SESSION_EVIDENCE = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_HOLY_GRAIL_V0_1.json"
)
OUTPUT_JSON = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_2.json"
)

FAMILY_ID = "RASCHKE_HOLY_GRAIL_PULLBACK"
CONTRACT_ID = "PC-RASCHKE-HOLY-GRAIL-PULLBACK-DRAFT-V0-2"
RESEARCH_LINEAGE_ID = "L-RAS-HOLYGRAIL"
SCHEMA_VERSION = "0.2"
CONTRACT_VERSION = "0.2.0"
CREATED_AT = "2026-08-20T00:00:00Z"
SOURCE_SCOPE = "US_EQUITIES_AND_US_INDEX"
DATA_EXPOSURE_HISTORY_REFERENCE = (
    "docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_HOLY_GRAIL_V0_1.json"
)

UNRESOLVED_OWNER_GATES = tuple(f"FGH-GATE-{number:02d}" for number in range(1, 7))
UNRESOLVED_MACHINE_DEFINITIONS = (
    "EXIT_ON_PUSH_TO_NEW_HIGHS_MACHINE_DEFINITION",
    "NEWLY_FORMED_SWING_LOW_MACHINE_DEFINITION",
    "TRAILING_STOP_MACHINE_DEFINITION",
)

_CLAIM_STATUS = {
    "EXPLICIT": ClaimStatus.EXPLICIT,
    "INFERRED": ClaimStatus.INFERRED,
    "UNKNOWN": ClaimStatus.UNKNOWN,
}


def _load_session_evidence() -> dict[str, Any]:
    try:
        payload = json.loads(SESSION_EVIDENCE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("Holy Grail SOURCE_ONLY evidence is unavailable or invalid") from error
    if not isinstance(payload.get("claims"), list) or not isinstance(payload.get("session"), dict):
        raise ValueError("Holy Grail SOURCE_ONLY evidence has an invalid structure")
    if len(payload["claims"]) != payload.get("recorded_claim_count"):
        raise ValueError("Holy Grail SOURCE_ONLY claim count does not match its evidence")
    return payload


def _source_claims(payload: dict[str, Any]) -> tuple[SourceClaimRef, ...]:
    claims: list[SourceClaimRef] = []
    for record in payload["claims"]:
        try:
            status = _CLAIM_STATUS[record["claim_status"]]
            claim = SourceClaimRef(
                claim_id=record["claim_id"],
                source_id=record["material_id"],
                source_anchor=record["source_anchor"],
                claim_status=status,
            )
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("Holy Grail SOURCE_ONLY claim record is invalid") from error
        claims.append(claim)
    if len({claim.claim_id for claim in claims}) != len(claims):
        raise ValueError("Holy Grail SOURCE_ONLY claim ids must be unique")
    return tuple(claims)


def _interpretations() -> tuple[InterpretationBranch, ...]:
    """Preserve pinned facts and unresolved questions without selecting PRIMARY."""
    return (
        InterpretationBranch(
            branch_id="SOURCE-PINNED-ADX-EMA-CONCEPTS",
            source_claim_ids=(
                "C-RAS-HG-SEM-002",
                "C-RAS-HG-SEM-003",
                "C-RAS-HG-SEM-004",
                "C-RAS-HG-SEM-005",
                "C-RAS-HG-SEM-006",
            ),
            source_basis=(
                "Source-pinned facts only: 14-period ADX, initially greater than 30 and rising, "
                "and the 20-period EMA concept. Numeric algorithms and timing remain unresolved."
            ),
            transfer_status=TransferStatus.EXPLICIT,
        ),
        InterpretationBranch(
            branch_id="SOURCE-PINNED-ENTRY-RISK-EXIT-CONCEPTS",
            source_claim_ids=(
                "C-RAS-HG-SEM-009",
                "C-RAS-HG-SEM-010",
                "C-RAS-HG-SEM-013",
                "C-RAS-HG-SEM-015",
                "C-RAS-HG-SEM-016",
                "C-RAS-HG-SEM-017",
                "C-RAS-HG-SEM-019",
            ),
            source_basis=(
                "Source-pinned concepts only: EMA pullback/touch, buy stop above the previous-bar "
                "high, protective stop at the newly formed swing low once filled, trailing stops, "
                "and exit on a push to new highs. Machine definitions remain unresolved."
            ),
            transfer_status=TransferStatus.EXPLICIT,
        ),
        InterpretationBranch(
            branch_id="SOURCE-PINNED-MULTI-TIMEFRAME-CONCEPT",
            source_claim_ids=("C-RAS-HG-SEM-024",),
            source_basis=(
                "The source is explicitly multi-timeframe, including base, 30, 60 and 120 minute "
                "contexts; it does not pin a single project PRIMARY timeframe."
            ),
            transfer_status=TransferStatus.EXPLICIT,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-FGH-GATE-01-EMA-PRICE-AND-TOUCH",
            source_claim_ids=("C-RAS-HG-SEM-007", "C-RAS-HG-SEM-009"),
            source_basis="EMA price basis and exact touch/penetration semantics are not source-pinned.",
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-FGH-GATE-02-ADX-RISING-SEQUENCE",
            source_claim_ids=("C-RAS-HG-SEM-004",),
            source_basis="The rising window and its timing relative to the pullback are not pinned.",
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-FGH-GATE-03-NUMERIC-POLICY",
            source_claim_ids=("C-RAS-HG-SEM-002", "C-RAS-HG-SEM-005"),
            source_basis="EMA seed, ADX initialization, precision and quantization are machine choices.",
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-FGH-GATE-04-TOUCH-ENTRY-ORDERING",
            source_claim_ids=("C-RAS-HG-SEM-009", "C-RAS-HG-SEM-010"),
            source_basis="One-minute OHLC cannot order a same-bar EMA touch and entry-stop trigger.",
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-FGH-GATE-05-FILL-PROTECTIVE-STOP-CHRONOLOGY",
            source_claim_ids=("C-RAS-HG-SEM-015", "C-RAS-HG-SEM-016"),
            source_basis="One-minute OHLC cannot order entry fill and protective-stop touch in one bar.",
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-FGH-GATE-06-PRIMARY-TIMEFRAME",
            source_claim_ids=("C-RAS-HG-SEM-024",),
            source_basis="The multi-timeframe source does not select one machine PRIMARY timeframe.",
            transfer_status=TransferStatus.UNKNOWN,
        ),
    )


def _observation_surfaces() -> tuple[ObservationSurface, ...]:
    return (
        ObservationSurface(
            surface_id="ADX_OHLC_DERIVED",
            required=True,
            observability_status=ObservabilityStatus.OBSERVABLE_NOW,
        ),
        ObservationSurface(
            surface_id="EMA_OHLC_DERIVED",
            required=True,
            observability_status=ObservabilityStatus.OBSERVABLE_NOW,
        ),
        ObservationSurface(
            surface_id="ENTRY_AND_PROTECTIVE_STOP_CHRONOLOGY",
            required=True,
            observability_status=ObservabilityStatus.PARTIALLY_OBSERVABLE,
            missing_inputs=("intrabar_ordering_at_one_minute",),
        ),
        ObservationSurface(
            surface_id="SWING_TRAILING_AND_EXIT_MACHINE_DEFINITIONS",
            required=True,
            observability_status=ObservabilityStatus.PARTIALLY_OBSERVABLE,
            missing_inputs=UNRESOLVED_MACHINE_DEFINITIONS,
        ),
    )


def build_contract() -> PlaybookContract:
    payload = _load_session_evidence()
    session = payload["session"]
    required_session_fields = (
        "source_bundle_identity",
        "source_bundle_hash",
        "session_identity",
    )
    if any(not isinstance(session.get(field), str) or not session[field] for field in required_session_fields):
        raise ValueError("Holy Grail SOURCE_ONLY session identity is incomplete")
    return PlaybookContract(
        schema_version=SCHEMA_VERSION,
        contract_version=CONTRACT_VERSION,
        contract_id=CONTRACT_ID,
        research_lineage_id=RESEARCH_LINEAGE_ID,
        family_id=FAMILY_ID,
        source_claims=_source_claims(payload),
        source_bundle_identity=session["source_bundle_identity"],
        source_bundle_hash=session["source_bundle_hash"],
        source_only_session_identity=session["session_identity"],
        source_scope=SOURCE_SCOPE,
        interpretations=_interpretations(),
        ambiguity_status=AmbiguityStatus.UNRESOLVED_CRITICAL,
        ambiguity_notes=(
            "FGH-GATE-01..06 and the required swing-low, trailing-stop, and exit-on-new-highs "
            "machine definitions remain unresolved. No implementation convention is PRIMARY."
        ),
        primary_required=True,
        source_variant_count=1,
        observation_surfaces=_observation_surfaces(),
        unavailable_inputs=(),
        instrument_scope=("ag", "al", "au", "cu", "ni", "rb"),
        timeframe_scope=("120MIN", "30MIN", "60MIN", "BASE"),
        project_transfer_status=TransferStatus.INFERRED,
        machine=None,
        data_exposure_history_reference=DATA_EXPOSURE_HISTORY_REFERENCE,
        created_at=CREATED_AT,
    )


def build_payload() -> dict[str, Any]:
    evidence = _load_session_evidence()
    contract = build_contract()
    validation = validate_contract(contract)
    return {
        "artifact": "RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_2",
        "schema_version": contract.schema_version,
        "contract_version": contract.contract_version,
        "contract_id": contract.contract_id,
        "contract_identity": contract.contract_identity,
        "research_lineage_id": contract.research_lineage_id,
        "family_id": contract.family_id,
        "source_scope": contract.source_scope,
        "project_transfer_status": contract.project_transfer_status.value,
        "source_bundle_identity": contract.source_bundle_identity,
        "source_bundle_hash": contract.source_bundle_hash,
        "source_only_session_identity": contract.source_only_session_identity,
        "source_claims": [
            {
                "claim_id": claim.claim_id,
                "source_id": claim.source_id,
                "source_anchor": claim.source_anchor,
                "claim_status": claim.claim_status.value,
                "claim_identity": claim.claim_identity,
            }
            for claim in contract.source_claims
        ],
        "interpretations": [
            {
                "branch_id": branch.branch_id,
                "source_claim_ids": list(branch.source_claim_ids),
                "source_basis": branch.source_basis,
                "transfer_status": branch.transfer_status.value,
                "primary_selected": branch.primary_selected,
                "branch_identity": branch.branch_identity,
            }
            for branch in contract.interpretations
        ],
        "observation_surfaces": [
            {
                "surface_id": surface.surface_id,
                "required": surface.required,
                "observability_status": surface.observability_status.value,
                "missing_inputs": list(surface.missing_inputs),
                "surface_identity": surface.surface_identity,
            }
            for surface in contract.observation_surfaces
        ],
        "ambiguity_status": contract.ambiguity_status.value,
        "ambiguity_notes": contract.ambiguity_notes,
        "instrument_scope": list(contract.instrument_scope),
        "timeframe_scope": list(contract.timeframe_scope),
        "machine_operationalization": None,
        "machine_readiness": validation.readiness.value,
        "machine_readiness_blockers": list(validation.blockers),
        "unresolved_owner_gates": list(UNRESOLVED_OWNER_GATES),
        "unresolved_machine_definitions": list(UNRESOLVED_MACHINE_DEFINITIONS),
        "source_evidence_recorded_claim_count": evidence["recorded_claim_count"],
        "final_decision": {
            "MACHINE_READY": "NO",
            "PRIMARY_FREEZE_READY": "NO",
            "STRATEGY_IDENTITY_CREATED": "NO",
            "OUTCOME_TEST_REGISTERED": "NO",
            "CANDIDATE_OUTCOME_DATA_USED": "NO",
        },
    }


def main() -> None:
    payload = build_payload()
    if payload["machine_readiness"] != "NOT_MACHINE_READY":
        raise SystemExit("Holy Grail draft unexpectedly became machine ready")
    OUTPUT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

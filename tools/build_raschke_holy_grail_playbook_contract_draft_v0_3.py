"""Build the source-faithful Holy Grail V0.3 Playbook Contract draft.

V0.3 is a current clarified pre-outcome draft.  It incorporates ONLY the
Owner-approved F/G/H decisions recorded in
``docs/reviews/FGH_SEMANTIC_GATE_OWNER_APPROVAL_2026-08-20.md`` while it:

- preserves the existing V0.2 / SOURCE_ONLY source-faithful claim corpus and
  provenance unchanged (SOURCE CLAIM layer);
- keeps the historical V0.2 draft/artifacts and builder untouched;
- labels every Owner-approved machine convention as a project INFERRED
  interpretation, never as a source claim (PROJECT INTERPRETATION layer);
- leaves every still-open operationalization prerequisite explicit and
  fail-closed (no machine layer, so the draft stays NOT_MACHINE_READY).

No candidate outcome access, StrategyIdentity creation, outcome-test
registration, or validation/final-holdout/shadow access is performed here.
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
    / "RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_3.json"
)

FAMILY_ID = "RASCHKE_HOLY_GRAIL_PULLBACK"
CONTRACT_ID = "PC-RASCHKE-HOLY-GRAIL-PULLBACK-DRAFT-V0-3"
PARENT_CONTRACT_ID = "PC-RASCHKE-HOLY-GRAIL-PULLBACK-DRAFT-V0-2"
RESEARCH_LINEAGE_ID = "L-RAS-HOLYGRAIL"
SCHEMA_VERSION = "0.3"
CONTRACT_VERSION = "0.3.0"
CREATED_AT = "2026-08-21T00:00:00Z"
SOURCE_SCOPE = "US_EQUITIES_AND_US_INDEX"
DATA_EXPOSURE_HISTORY_REFERENCE = (
    "docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_HOLY_GRAIL_V0_1.json"
)

# Owner-approved F/G/H decisions only (FGH_SEMANTIC_GATE_OWNER_APPROVAL_2026-08-20.md).
# Every decision is a project INFERRED machine convention; none is a source claim.
FGH_APPROVED_DECISIONS: dict[str, dict[str, str]] = {
    "EMA_TOUCH": {
        "EMA_PERIOD": "20",
        "EMA_PRICE_BASIS": "PROJECT_INFERRED_CLOSE",
        "EMA_REFERENCE": "PRIOR_COMPLETED_BAR_AVAILABLE",
        "TOUCH_RULE": "BAR_LOW_LE_EMA_PRIOR_LE_BAR_HIGH",
        "CURRENT_BAR_CLOSE_LOOKAHEAD": "FORBIDDEN",
    },
    "ADX": {
        "ADX_PERIOD": "14",
        "ADX_THRESHOLD": ">30",
        "ADX_CONTEXT": "INITIAL_PRE_PULLBACK",
        "TOUCH_BAR_RISING_REQUIRED": "NO",
        "OLD_TOUCH_BAR_ONE_STEP_RULE": "NOT_AUTHORITY",
        "ADX_RISING_WINDOW": "OPEN_VERSIONED_NON_OUTCOME_CHOICE",
    },
    "NUMERIC_POLICY": {
        "EMA_SEED": "SMA",
        "ADX_INITIALIZATION": "WILDER_SMA_DX",
        "ARITHMETIC": "DECIMAL",
        "QUANTIZATION": "6DP_ROUND_HALF_UP",
        "NUMERIC_POLICY": "VERSIONED_IDENTITY_BOUND",
    },
    "SAME_BAR_TOUCH_ENTRY": {
        "SAME_BAR_TOUCH_ENTRY": "AMBIGUOUS_INTRABAR_SEQUENCE",
        "FAIL_CLOSED": "YES",
    },
    "FILL_PROTECTIVE_STOP_CHRONOLOGY": {
        "CHRONOLOGY": "COMPLETED_BAR_AVAILABILITY_CONSERVATIVE",
        "EXCHANGE_RESTING_CLAIM": "NO",
        "SAME_BAR_FILL_STOP": "AMBIGUOUS_INTRABAR_SEQUENCE",
        "NEXT_BAR_ONLY_STOP_ACTIVATION_DEFAULT": "REJECTED",
        "INTRABAR_ORDERING": "NOT_OBSERVABLE_AT_1M",
    },
    "TIMEFRAME": {
        "PRIMARY_TIMEFRAME_BRANCH": "BASE",
        "SOURCE_ALTERNATIVES": "30MIN,60MIN,120MIN",
        "BASE_TO_MACHINE_INTERVAL": "OPEN",
    },
    "SWING_LOW_HIGH": {
        "SWING_DEFINITION": "FRACTAL_PIVOT_EXPLICIT_CONFIRMATION",
        "RIGHT_SIDE_CONFIRMATION_REQUIRED": "YES",
        "SAME_BAR_AVAILABILITY": "NO",
        "SHORT_SIDE": "MIRROR_SWING_HIGH",
        "SWING_CONFIRMATION_COUNTS": "OPEN_VERSIONED_NON_OUTCOME_CHOICE",
    },
    "TRAILING_STOP": {
        "TRAILING_STOP_MACHINE_DEFINITION": "NOT_ADOPTED",
        "MACHINE_READY_BLOCKER": "PRESERVE",
        "OUTCOME_TUNING_FOR_TRAILING": "FORBIDDEN",
    },
    "EXIT_ON_PUSH_TO_NEW_HIGHS": {
        "EXIT_ON_PUSH_TO_NEW_HIGHS": "OPTIONAL_VERSIONED_VARIANT",
        "PRIMARY_EXIT_REPLACED": "NO",
        "OUTCOME_RESCUE": "FORBIDDEN",
    },
}

# Still-open operationalization prerequisites (never solved by this artifact).
OPEN_PREREQUISITES: dict[str, str] = {
    "HOLY_GRAIL_BASE_TO_MACHINE_INTERVAL": "OPEN",
    "HOLY_GRAIL_ADX_RISING_WINDOW": "OPEN_VERSIONED_NON_OUTCOME_CHOICE",
    "HOLY_GRAIL_SWING_CONFIRMATION_COUNTS": "OPEN_VERSIONED_NON_OUTCOME_CHOICE",
    "HOLY_GRAIL_TRAILING_STOP_MACHINE_DEFINITION": "NOT_ADOPTED",
}

UNRESOLVED_MACHINE_DEFINITIONS = (
    "BASE_TO_MACHINE_INTERVAL",
    "ADX_RISING_WINDOW",
    "SWING_CONFIRMATION_COUNTS",
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
    """Preserve pinned source facts and record the Owner-approved F/G/H
    conventions (INFERRED) while leaving open prerequisites explicit."""
    return (
        # ---- SOURCE-pinned branches (EXPLICIT; unchanged from V0.2) ----
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
        # ---- Owner-approved F/G/H conventions (project INFERRED) ----
        InterpretationBranch(
            branch_id="FGH-DECIDED-EMA-TOUCH-CONVENTION",
            source_claim_ids=("C-RAS-HG-SEM-005", "C-RAS-HG-SEM-006", "C-RAS-HG-SEM-009"),
            source_basis=(
                "Owner-approved FGH-GATE-01 (2026-08-20), project INFERRED machine convention: "
                "EMA_PERIOD=20; EMA_PRICE_BASIS=PROJECT_INFERRED_CLOSE (not a source claim; "
                "the source does not pin an EMA price basis); EMA_REFERENCE=PRIOR_COMPLETED_BAR_AVAILABLE; "
                "TOUCH_RULE=BAR_LOW_LE_EMA_PRIOR_LE_BAR_HIGH; CURRENT_BAR_CLOSE_LOOKAHEAD=FORBIDDEN. "
                "A bar may test low <= EMA_prior <= high only against an EMA already available from "
                "prior completed bars; the current bar's close must not judge the same bar's touch."
            ),
            transfer_status=TransferStatus.INFERRED,
        ),
        InterpretationBranch(
            branch_id="FGH-DECIDED-ADX-PRE-PULLBACK-CONTEXT",
            source_claim_ids=("C-RAS-HG-SEM-002", "C-RAS-HG-SEM-003", "C-RAS-HG-SEM-004"),
            source_basis=(
                "Owner-approved FGH-GATE-02 (2026-08-20): source period/threshold preserved "
                "(ADX_PERIOD=14; ADX_THRESHOLD=>30); ADX_CONTEXT=INITIAL_PRE_PULLBACK; "
                "TOUCH_BAR_RISING_REQUIRED=NO; OLD_TOUCH_BAR_ONE_STEP_RULE=NOT_AUTHORITY; "
                "ADX_RISING_WINDOW=OPEN_VERSIONED_NON_OUTCOME_CHOICE (still unresolved; the exact "
                "deterministic rising window is not chosen by this artifact)."
            ),
            transfer_status=TransferStatus.INFERRED,
        ),
        InterpretationBranch(
            branch_id="FGH-DECIDED-NUMERIC-POLICY",
            source_claim_ids=("C-RAS-HG-SEM-002", "C-RAS-HG-SEM-005"),
            source_basis=(
                "Owner-approved FGH-GATE-03 (2026-08-20) engineering convention, project INFERRED "
                "machine fact (not a source fact): EMA_SEED=SMA; ADX_INITIALIZATION=WILDER_SMA_DX; "
                "ARITHMETIC=DECIMAL; QUANTIZATION=6DP_ROUND_HALF_UP; NUMERIC_POLICY=VERSIONED_IDENTITY_BOUND."
            ),
            transfer_status=TransferStatus.INFERRED,
        ),
        InterpretationBranch(
            branch_id="FGH-DECIDED-SAME-BAR-TOUCH-ENTRY",
            source_claim_ids=("C-RAS-HG-SEM-009", "C-RAS-HG-SEM-010"),
            source_basis=(
                "Owner-approved FGH-GATE-04 (2026-08-20): SAME_BAR_TOUCH_ENTRY="
                "AMBIGUOUS_INTRABAR_SEQUENCE; FAIL_CLOSED=YES. At 1-minute resolution, if the EMA "
                "touch and the entry-stop threshold are both reached inside the same bar and their "
                "ordering is not observable, fail closed; no intrabar ordering is invented."
            ),
            transfer_status=TransferStatus.INFERRED,
        ),
        InterpretationBranch(
            branch_id="FGH-DECIDED-FILL-PROTECTIVE-STOP-CHRONOLOGY",
            source_claim_ids=("C-RAS-HG-SEM-015", "C-RAS-HG-SEM-016"),
            source_basis=(
                "Owner-approved FGH-GATE-05 (2026-08-20): CHRONOLOGY="
                "COMPLETED_BAR_AVAILABILITY_CONSERVATIVE; EXCHANGE_RESTING_CLAIM=NO; "
                "SAME_BAR_FILL_STOP=AMBIGUOUS_INTRABAR_SEQUENCE; "
                "NEXT_BAR_ONLY_STOP_ACTIVATION_DEFAULT=REJECTED; INTRABAR_ORDERING=NOT_OBSERVABLE_AT_1M."
            ),
            transfer_status=TransferStatus.INFERRED,
        ),
        InterpretationBranch(
            branch_id="FGH-DECIDED-TIMEFRAME-BASE-BRANCH",
            source_claim_ids=("C-RAS-HG-SEM-024",),
            source_basis=(
                "Owner-approved FGH-GATE-06 (2026-08-20): PRIMARY_TIMEFRAME_BRANCH=BASE; "
                "SOURCE_ALTERNATIVES=30MIN,60MIN,120MIN; BASE_TO_MACHINE_INTERVAL=OPEN "
                "(still unresolved; BASE is not mapped to any concrete machine interval by this artifact)."
            ),
            transfer_status=TransferStatus.INFERRED,
        ),
        InterpretationBranch(
            branch_id="FGH-DECIDED-SWING-LOW-DEFINITION",
            source_claim_ids=("C-RAS-HG-SEM-015",),
            source_basis=(
                "Owner-approved swing decision (2026-08-20), project INFERRED machine convention: "
                "SWING_DEFINITION=FRACTAL_PIVOT_EXPLICIT_CONFIRMATION; RIGHT_SIDE_CONFIRMATION_REQUIRED=YES; "
                "SAME_BAR_AVAILABILITY=NO; SHORT_SIDE=MIRROR_SWING_HIGH; "
                "SWING_CONFIRMATION_COUNTS=OPEN_VERSIONED_NON_OUTCOME_CHOICE "
                "(still unresolved; left/right confirmation counts are not chosen by this artifact)."
            ),
            transfer_status=TransferStatus.INFERRED,
        ),
        InterpretationBranch(
            branch_id="FGH-DECIDED-TRAILING-STOP-NOT-ADOPTED",
            source_claim_ids=("C-RAS-HG-SEM-017",),
            source_basis=(
                "Owner-approved trailing decision (2026-08-20): TRAILING_STOP_MACHINE_DEFINITION="
                "NOT_ADOPTED; MACHINE_READY_BLOCKER=PRESERVE; OUTCOME_TUNING_FOR_TRAILING=FORBIDDEN. "
                "The source statement equivalent to 'trail stops as profits grow' does not authorize "
                "inventing ATR, percentage, swing, EMA, breakeven, fixed-step or other trailing mechanics."
            ),
            transfer_status=TransferStatus.INFERRED,
        ),
        InterpretationBranch(
            branch_id="FGH-DECIDED-EXIT-NEW-HIGHS-OPTIONAL",
            source_claim_ids=("C-RAS-HG-SEM-019",),
            source_basis=(
                "Owner-approved exit decision (2026-08-20): EXIT_ON_PUSH_TO_NEW_HIGHS="
                "OPTIONAL_VERSIONED_VARIANT; PRIMARY_EXIT_REPLACED=NO; OUTCOME_RESCUE=FORBIDDEN. "
                "The later source wording about exit on a push to new highs is an optional versioned "
                "variant, not the Holy Grail PRIMARY exit."
            ),
            transfer_status=TransferStatus.INFERRED,
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
            surface_id="SWING_LOW_CONFIRMATION",
            required=True,
            observability_status=ObservabilityStatus.PARTIALLY_OBSERVABLE,
            missing_inputs=("swing_confirmation_counts",),
        ),
        ObservationSurface(
            surface_id="TRAILING_STOP_MACHINE_DEFINITION",
            required=True,
            observability_status=ObservabilityStatus.PARTIALLY_OBSERVABLE,
            missing_inputs=("trailing_stop_machine_definition",),
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
            "FGH-GATE-01..06 and the swing/trailing/exit machine conventions are Owner-decided "
            "(2026-08-20). The remaining operationalization prerequisites - BASE-to-machine "
            "interval, ADX rising window, swing confirmation counts, and trailing-stop machine "
            "definition - remain unresolved. No implementation convention is PRIMARY."
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
        parent_contract_id=PARENT_CONTRACT_ID,
        created_at=CREATED_AT,
    )


def build_payload() -> dict[str, Any]:
    evidence = _load_session_evidence()
    contract = build_contract()
    validation = validate_contract(contract)
    return {
        "artifact": "RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_3",
        "schema_version": contract.schema_version,
        "contract_version": contract.contract_version,
        "contract_id": contract.contract_id,
        "contract_identity": contract.contract_identity,
        "parent_contract_id": contract.parent_contract_id,
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
        "fgh_approved_decisions": dict(FGH_APPROVED_DECISIONS),
        "open_prerequisites": dict(OPEN_PREREQUISITES),
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
        raise SystemExit("Holy Grail V0.3 draft unexpectedly became machine ready")
    if payload["final_decision"]["MACHINE_READY"] != "NO":
        raise SystemExit("Holy Grail V0.3 draft final decision is not fail-closed")
    OUTPUT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

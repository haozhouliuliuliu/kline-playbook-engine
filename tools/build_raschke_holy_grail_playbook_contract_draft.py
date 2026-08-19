"""RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_1 - deterministic builder.

Lane F (HOLY_GRAIL_PLAYBOOK_CONTRACT_INTERPRETATION_FREEZE_ENGINEER).

Converts the accepted Raschke Holy Grail source semantics into a real versioned
Playbook Contract DRAFT using the actual generic `src.playbook_contract.py`
schema (SOURCE CLAIM != PROJECT INTERPRETATION != MACHINE OPERATIONALIZATION).
This is a pre-outcome specification task, NOT a backtest, NOT outcome
inspection, NOT parameter tuning, NOT statistical inference.

This builder:

- binds the exact accepted Holy Grail SOURCE_ONLY claim records
  (C-RAS-HG-SEM-001..027) from
  `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_HOLY_GRAIL_V0_1.json`
  (source IDs, anchors, statuses) plus the source-bundle identity/hash and the
  SOURCE_ONLY session identity from the accepted evidence;
- constructs the PROJECT INTERPRETATION layer as `InterpretationBranch` objects
  with explicit predeclared `PROJECT_INFERRED_PREDECLARED` conventions and the
  source-explicit mirror concept;
- declares the required `ObservationSurface` objects with point-in-time
  observability;
- does NOT add a `MachineOperationalization` (Lane G/H machine dependencies are
  not merged; the source/interpretation contract may remain NOT_MACHINE_READY);
- runs the real `validate_contract(...)` and records the exact blockers;
- writes the complete deterministic contract representation to
  `docs/evidence/RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_1.json`.

HARD BOUNDARIES:
- NO candidate market outcomes, PnL, returns, expectancy, win rate, Sharpe,
  equity/drawdown, Validation, or historical final-holdout access.
- No real `StrategyIdentity` is created; nothing is registered in any
  `StrategyCatalog`; no `ResearchFirewall` outcome access is requested.
- No invented source claims; every `SourceClaimRef` comes from the accepted
  SOURCE_ONLY evidence.
- Unresolved critical interpretation fields remain UNRESOLVED_CRITICAL
  (PRIMARY_FREEZE_READY=NO / AMBIGUOUS_STOP=YES) rather than being resolved by
  guessing or outcome selection.

Run:
    python -m tools.build_raschke_holy_grail_playbook_contract_draft
"""

from __future__ import annotations

import json
from pathlib import Path

from src.playbook_contract import (
    AmbiguityStatus,
    ClaimStatus,
    InterpretationBranch,
    MachineReadiness,
    ObservationSurface,
    ObservabilityStatus,
    PlaybookContract,
    SourceClaimRef,
    TransferStatus,
    validate_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Identity constants (accepted authority)
# ---------------------------------------------------------------------------

FAMILY_ID = "RASCHKE_HOLY_GRAIL_PULLBACK"
CONTRACT_ID = "PC-RASCHKE-HOLY-GRAIL-PULLBACK-DRAFT-V0-1"
RESEARCH_LINEAGE_ID = "L-RAS-HOLYGRAIL"
SCHEMA_VERSION = "0.1"
CONTRACT_VERSION = "0.1.0"
CREATED_AT = "2026-08-20T00:00:00Z"
SOURCE_SCOPE = "US_EQUITIES_AND_US_INDEX"
DATA_EXPOSURE_HISTORY_REFERENCE = (
    "docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_HOLY_GRAIL_V0_1.json"
)

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
    / "RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_1.json"
)

_CLAIM_STATUS_MAP = {
    "EXPLICIT": ClaimStatus.EXPLICIT,
    "INFERRED": ClaimStatus.INFERRED,
    "UNKNOWN": ClaimStatus.UNKNOWN,
}

# ---------------------------------------------------------------------------
# Source claim binding (read from accepted SOURCE_ONLY evidence; no invention)
# ---------------------------------------------------------------------------


def _load_source_claims() -> tuple[SourceClaimRef, ...]:
    """Bind the exact accepted Holy Grail SOURCE_ONLY claim records."""
    with SESSION_EVIDENCE.open("r", encoding="utf-8") as handle:
        session_doc = json.load(handle)
    session = session_doc["session"]

    claims: list[SourceClaimRef] = []
    for record in session_doc["claims"]:
        status_value = record["claim_status"]
        if status_value not in _CLAIM_STATUS_MAP:
            raise ValueError(f"unknown claim status: {status_value}")
        claims.append(
            SourceClaimRef(
                claim_id=record["claim_id"],
                source_id=record["material_id"],
                source_anchor=record["source_anchor"],
                claim_status=_CLAIM_STATUS_MAP[status_value],
            )
        )

    if len(claims) != session_doc["recorded_claim_count"]:
        raise ValueError("source claim count mismatch")
    return (
        claims,
        {
            "source_bundle_identity": session["source_bundle_identity"],
            "source_bundle_hash": session["source_bundle_hash"],
            "source_only_session_identity": session["session_id"],
            "session_identity": session["session_identity"],
            "verification_evidence": session["verification_evidence"],
        },
    )


# ---------------------------------------------------------------------------
# PROJECT INTERPRETATION layer (predeclared, versioned, labeled INFERRED)
# ---------------------------------------------------------------------------


def _interpretations() -> tuple[InterpretationBranch, ...]:
    """Predeclared project interpretation branches (no PRIMARY; AMBIGUOUS_STOP)."""
    return (
        InterpretationBranch(
            branch_id="INT-EMA-PRICE-INPUT-CLOSE",
            source_claim_ids=("C-RAS-HG-SEM-007",),
            source_basis=(
                "MOVING_AVERAGE_PRICE_INPUT is NOT_PINNED by the source; "
                "close-based EMA adopted as the standard software/math convention."
            ),
            transfer_status=TransferStatus.INFERRED,
            primary_selected=False,
            interpretation_note=(
                "PROJECT_INFERRED_PREDECLARED: EMA_PRICE_INPUT=close. Reason: the "
                "source never states the EMA price basis; a close-based EMA is the "
                "genuinely unambiguous standard software/math convention and is "
                "clearly labeled INFERRED, never a source claim."
            ),
        ),
        InterpretationBranch(
            branch_id="INT-EMA-TOUCH-INTRABAR",
            source_claim_ids=("C-RAS-HG-SEM-009", "C-RAS-HG-SEM-010"),
            source_basis=(
                "PULLBACK_TOUCH_OR_PENETRATION_RULE / ENTRY_TRIGGER: source says "
                "'when price touches the 20-period MA'; the bar-level touch "
                "definition is not pinned."
            ),
            transfer_status=TransferStatus.INFERRED,
            primary_selected=False,
            interpretation_note=(
                "PROJECT_INFERRED_PREDECLARED: EMA_TOUCH_BAR_SEMANTICS = "
                "bar.low <= EMA <= bar.high (long side). This is a project machine "
                "interpretation of 'touch', not a source-exact definition."
            ),
        ),
        InterpretationBranch(
            branch_id="INT-ADX-RISING-1BAR",
            source_claim_ids=("C-RAS-HG-SEM-004",),
            source_basis=(
                "ADX_RISING_OR_LEVEL_REQUIREMENT: source requires 'initially greater "
                "than 30 and rising'; the slope measurement window is not pinned."
            ),
            transfer_status=TransferStatus.INFERRED,
            primary_selected=False,
            interpretation_note=(
                "PROJECT_INFERRED_PREDECLARED: ADX_RISING_MACHINE_SEMANTICS = "
                "ADX[current] > ADX[previous] at the context bar (minimal literal "
                "deterministic reading, clearly labeled INFERRED)."
            ),
        ),
        InterpretationBranch(
            branch_id="INT-ENTRY-OFFSET-1TICK",
            source_claim_ids=("C-RAS-HG-SEM-012", "C-RAS-HG-SEM-010"),
            source_basis=(
                "ENTRY_OFFSET / ENTRY_TRIGGER: source says buy stop 'above the high "
                "of the previous bar'; the tick offset above that high is not stated."
            ),
            transfer_status=TransferStatus.INFERRED,
            primary_selected=False,
            interpretation_note=(
                "PROJECT_INFERRED_PREDECLARED: ENTRY_ABOVE_PREVIOUS_HIGH_TICK_OFFSET "
                "= minimal legal price one tick above the previous-bar high, derived "
                "from governed contract tick metadata. This is a project operational "
                "convention; the source does not say 'one tick'."
            ),
        ),
        InterpretationBranch(
            branch_id="INT-STOP-ACTIVATION-AFTER-FILL",
            source_claim_ids=("C-RAS-HG-SEM-015", "C-RAS-HG-SEM-016"),
            source_basis=(
                "INITIAL_STOP / POST_ENTRY_INVALIDATION: source says 'Once filled, "
                "enter a protective sell stop at the newly formed swing low'; the "
                "activation timing after fill is not separately pinned."
            ),
            transfer_status=TransferStatus.INFERRED,
            primary_selected=False,
            interpretation_note=(
                "PROJECT_INFERRED_PREDECLARED: PROTECTIVE_STOP_ACTIVATION_TIME = "
                "protective stop active from the first eligible future bar after the "
                "entry fill (no same-bar-before-fill activation; consistent with the "
                "generic stop-trigger 'first eligible future bar' convention)."
            ),
        ),
        InterpretationBranch(
            branch_id="INT-SESSION-OFFICIAL-TRADING-DAY",
            source_claim_ids=("C-RAS-HG-SEM-024",),
            source_basis=(
                "TIMEFRAME_SCOPE: the source is silent on session boundary; the "
                "project governs official trading-day identity via SessionMetadata."
            ),
            transfer_status=TransferStatus.INFERRED,
            primary_selected=False,
            interpretation_note=(
                "PROJECT_INFERRED_PREDECLARED: SESSION_BOUNDARY = official trading-day "
                "identity from governed SessionMetadata, not civil-date inference "
                "(already-governed project fact)."
            ),
        ),
        InterpretationBranch(
            branch_id="INT-INSTRUMENT-SCOPE-6PRODUCTS",
            source_claim_ids=("C-RAS-HG-SEM-027", "C-RAS-HG-SEM-025"),
            source_basis=(
                "CURRENT_PROJECT_PRODUCT_TRANSFER / INSTRUMENT_SCOPE: source scope is "
                "US equities/US index; Chinese-futures support is UNKNOWN; transfer is "
                "INFERRED_PROJECT_TRANSFER."
            ),
            transfer_status=TransferStatus.INFERRED,
            primary_selected=False,
            interpretation_note=(
                "PROJECT_INFERRED_PREDECLARED: CURRENT_PROJECT_INSTRUMENT_SCOPE = "
                "cu,al,ni,au,ag,rb predeclared as the fixed project research scope "
                "BEFORE any outcome access; transfer is INFERRED, not source-explicit."
            ),
        ),
        InterpretationBranch(
            branch_id="INT-LONG-SHORT-MIRROR",
            source_claim_ids=("C-RAS-HG-SEM-014", "C-RAS-HG-SEM-013"),
            source_basis=(
                "SHORT_RULE 'sells reversed': the short side is the source's own "
                "reversal statement of the long 4-step rules."
            ),
            transfer_status=TransferStatus.EXPLICIT,
            primary_selected=False,
            interpretation_note=(
                "SOURCE_EXPLICIT mirror concept; machine mirror details (sell stop "
                "below previous-bar low, protective stop at newly formed swing high) "
                "inherit the unresolved swing-high machine definition."
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Observation surfaces (point-in-time observability)
# ---------------------------------------------------------------------------


def _observation_surfaces() -> tuple[ObservationSurface, ...]:
    return (
        ObservationSurface(
            surface_id="ADX_14_OHLC_DERIVED",
            required=True,
            observability_status=ObservabilityStatus.OBSERVABLE_NOW,
        ),
        ObservationSurface(
            surface_id="EMA_20_PRICE_DERIVED",
            required=True,
            observability_status=ObservabilityStatus.OBSERVABLE_NOW,
        ),
        ObservationSurface(
            surface_id="BAR_HIGH_LOW_ENTRY_STOP",
            required=True,
            observability_status=ObservabilityStatus.OBSERVABLE_NOW,
        ),
        ObservationSurface(
            surface_id="PRICE_POSITION_RANGE_MOMENTUM_HIGHS",
            required=True,
            observability_status=ObservabilityStatus.OBSERVABLE_NOW,
            missing_inputs=("range_boundary_inferred",),
        ),
        ObservationSurface(
            surface_id="TIMEFRAME_30_60_120_DERIVABLE",
            required=True,
            observability_status=ObservabilityStatus.OBSERVABLE_NOW,
            missing_inputs=("operating_timeframe_unresolved",),
        ),
        ObservationSurface(
            surface_id="NYSE_TICK_BREADTH",
            required=False,
            observability_status=ObservabilityStatus.NOT_OBSERVABLE_WITH_CURRENT_DATA,
            missing_inputs=("NYSE_BREADTH", "NYSE_TICK"),
        ),
    )


# ---------------------------------------------------------------------------
# Contract construction + validation
# ---------------------------------------------------------------------------

AMBIGUITY_NOTES = (
    "PRIMARY_FREEZE_READY=NO / AMBIGUOUS_STOP=YES. UNRESOLVED_CRITICAL_AMBIGUITY: "
    "5 machine-facing fields have multiple materially different equally-plausible "
    "interpretations that cannot be justified from source/documentary evidence "
    "alone and must NOT be resolved by outcome selection: "
    "(1) NEWLY_FORMED_SWING_LOW_MACHINE_DEFINITION (source pins the protective-stop "
    "reference concept 'newly formed swing low' but no software pivot algorithm; "
    "fractal/leg/zigzag pivot definitions remain equally plausible); "
    "(2) NEWLY_FORMED_SWING_HIGH_MACHINE_DEFINITION (mirror; same); "
    "(3) TRAILING_STOP_MACHINE_DEFINITION ('trail stops as profits grow'; "
    "swing/MA/distance-based trail mechanics equally plausible); "
    "(4) EXIT_ON_PUSH_TO_NEW_HIGHS_MACHINE_DEFINITION ('look to exit on a push to "
    "new highs'; the reference level and confirmation semantics are not pinned); "
    "(5) OPERATING_TIMEFRAME (source explicitly multi-timeframe: base chart then "
    "30/60/120-minute; no single operating timeframe is source-justified, and it is "
    "not hidden behind a tunable parameter). See "
    "docs/evidence/RASCHKE_HOLY_GRAIL_INTERPRETATION_FREEZE_V0_1.md for the "
    "preserved alternatives."
)


def build_contract() -> PlaybookContract:
    claims, bundle = _load_source_claims()
    return PlaybookContract(
        schema_version=SCHEMA_VERSION,
        contract_version=CONTRACT_VERSION,
        contract_id=CONTRACT_ID,
        research_lineage_id=RESEARCH_LINEAGE_ID,
        family_id=FAMILY_ID,
        source_claims=claims,
        source_bundle_identity=bundle["source_bundle_identity"],
        source_bundle_hash=bundle["source_bundle_hash"],
        source_only_session_identity=bundle["source_only_session_identity"],
        source_scope=SOURCE_SCOPE,
        interpretations=_interpretations(),
        ambiguity_status=AmbiguityStatus.UNRESOLVED_CRITICAL,
        ambiguity_notes=AMBIGUITY_NOTES,
        primary_required=True,
        source_variant_count=1,
        observation_surfaces=_observation_surfaces(),
        unavailable_inputs=("NYSE_BREADTH", "NYSE_TICK"),
        instrument_scope=("ag", "al", "au", "cu", "ni", "rb"),
        timeframe_scope=("120MIN", "30MIN", "60MIN", "BASE"),
        project_transfer_status=TransferStatus.INFERRED,
        machine=None,
        data_exposure_history_reference=DATA_EXPOSURE_HISTORY_REFERENCE,
        parent_contract_id=None,
        created_at=CREATED_AT,
    )


def _contract_full_dict(contract: PlaybookContract, session_bundle: dict) -> dict:
    """Complete deterministic representation (not merely a prose summary)."""
    result = validate_contract(contract)
    return {
        "artifact": "RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_1",
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
        "session_identity": session_bundle["session_identity"],
        "verification_evidence": session_bundle["verification_evidence"],
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
                "variant_label": branch.variant_label,
                "interpretation_note": branch.interpretation_note,
                "branch_identity": branch.branch_identity,
            }
            for branch in contract.interpretations
        ],
        "ambiguity_status": contract.ambiguity_status.value,
        "ambiguity_notes": contract.ambiguity_notes,
        "primary_required": contract.primary_required,
        "source_variant_count": contract.source_variant_count,
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
        "unavailable_inputs": list(contract.unavailable_inputs),
        "instrument_scope": list(contract.instrument_scope),
        "timeframe_scope": list(contract.timeframe_scope),
        "machine_operationalization": None,
        "data_exposure_history_reference": contract.data_exposure_history_reference,
        "parent_contract_id": contract.parent_contract_id,
        "created_at": contract.created_at,
        "machine_readiness": result.readiness.value,
        "machine_readiness_blockers": list(result.blockers),
        "contract_machine_ready": result.ready,
    }


def main() -> None:
    claims, bundle = _load_source_claims()
    contract = build_contract()
    result = validate_contract(contract)

    payload = _contract_full_dict(contract, bundle)
    payload["final_decision"] = {
        "STATUS": "COMPLETE",
        "FAMILY": FAMILY_ID,
        "PRIMARY_FREEZE_READY": "NO",
        "AMBIGUOUS_STOP": "YES",
        "TIMEFRAME_PRIMARY": "UNRESOLVED",
        "PROJECT_TRANSFER_STATUS": contract.project_transfer_status.value,
        "CONTRACT_MACHINE_READY": result.ready,
        "NO_CANDIDATE_OUTCOME_DATA_USED": "YES",
        "REAL_STRATEGY_IDENTITY_CREATED": "NO",
    }

    OUTPUT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"FAMILY={FAMILY_ID}")
    print(f"CONTRACT_IDENTITY={contract.contract_identity}")
    print(f"SOURCE_CLAIMS_BOUND={len(contract.source_claims)}")
    print(f"PROJECT_INTERPRETATIONS={len(contract.interpretations)}")
    print(f"SOURCE_EXPLICIT_FIELDS=0")
    print(f"PROJECT_INFERRED_FIELDS=7")
    print(f"UNRESOLVED_CRITICAL_FIELDS=5")
    print(f"TIMEFRAME_PRIMARY=UNRESOLVED")
    print(f"PROJECT_TRANSFER_STATUS={contract.project_transfer_status.value}")
    print(f"CONTRACT_MACHINE_READY={result.ready}")
    print("CONTRACT_VALIDATION_BLOCKERS=" + ",".join(result.blockers))
    print(f"WROTE={OUTPUT_JSON.relative_to(REPO_ROOT)}")
    if result.ready:
        raise SystemExit("unexpected: contract should NOT be machine-ready")
    if "UNRESOLVED_CRITICAL_AMBIGUITY" not in result.blockers:
        raise SystemExit("UNRESOLVED_CRITICAL_AMBIGUITY must be present and unhidden")


if __name__ == "__main__":
    main()

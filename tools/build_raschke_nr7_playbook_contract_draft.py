"""Build the source-faithful Raschke NR7 V0.1 Playbook Contract draft.

This is a mechanical translation of the accepted SOURCE_ONLY NR7
semantic-completion evidence
(``docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_NR7_SEMANTIC_V0_1.json``)
into a generic Playbook Contract DRAFT.  It preserves the three mandatory
layers separately:

    SOURCE CLAIM
    != PROJECT / AI INTERPRETATION
    != MACHINE OPERATIONALIZATION

It deliberately fails closed: the accepted evidence does not pin the post-entry
risk loop (``INITIAL_STOP=NOT_PINNED``, ``POST_ENTRY_INVALIDATION=NOT_PINNED``,
integration correction IC-1), does not justify a unique early-morning-range
PRIMARY (45-minute vs 60-minute are both SOURCE_PERMITTED variants), and leaves
order mechanics, exit/target, no-trade, and Chinese-futures session-boundary
conventions unresolved.  Therefore this draft never selects a PRIMARY, never
creates a StrategyIdentity, never registers an outcome test, and never requests
any ResearchFirewall candidate-outcome grant.

The Holy Grail builder/artifact is used as a STRUCTURAL implementation
reference only.  No Holy Grail trading semantics (ADX/EMA/swing-low/trailing
stop rules) are imported into NR7.

Hard prohibitions preserved here (do not relax):

- no candidate PnL / expectancy / Sharpe / win-loss / equity-curve / outcome
  trade-count diagnostics;
- no outcome-based selection between the 45-minute and 60-minute early-range
  variants;
- no invented OHLCV proxy for NYSE TICK / breadth / leadership;
- UNKNOWN stays UNKNOWN (never rewritten EXPLICIT).
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
    / "HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_NR7_SEMANTIC_V0_1.json"
)
OUTPUT_JSON = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "RASCHKE_NR7_PLAYBOOK_CONTRACT_DRAFT_V0_1.json"
)

FAMILY_ID = "RASCHKE_NR7_RANGE_CONTRACTION_TREND_DAY_BREAKOUT"
CONTRACT_ID = "PC-RASCHKE-NR7-RANGE-CONTRACTION-DRAFT-V0-1"
RESEARCH_LINEAGE_ID = "L-RAS-NR7"
SCHEMA_VERSION = "0.2"
CONTRACT_VERSION = "0.1.0"
CREATED_AT = "2026-08-21T00:00:00Z"
SOURCE_SCOPE = "US_EQUITY_INDEX_FUTURES_AND_US_EQUITIES_AND_COMMODITY_FUTURES"
DATA_EXPOSURE_HISTORY_REFERENCE = (
    "docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_NR7_SEMANTIC_V0_1.json"
)

# Source-permitted early-morning-range window variants (claim C-RAS-NR7-SEM-004,
# semantic_classification=SOURCE_PERMITTED_MULTIPLE_VARIANTS).  Neither variant
# is uniquely PRIMARY in the source; no outcome-based selection is permitted.
EARLY_RANGE_VARIANTS = (
    "EARLY_RANGE_VARIANT_45MIN",
    "EARLY_RANGE_VARIANT_60MIN",
)

# Semantic fields the accepted evidence records as NOT_PINNED or as an
# unresolved PARTIALLY_PINNED machine detail.  Preserved verbatim as unresolved.
UNRESOLVED_MACHINE_DEFINITIONS = (
    "CHINESE_FUTURES_DAILY_BAR_BOUNDARY",
    "CONFIRMATION_THRESHOLDS",
    "EARLY_MORNING_RANGE_PRIMARY_45MIN_VS_60MIN",
    "END_OF_SESSION_HANDLING",
    "ENTRY_OFFSET_OR_TICK_CONVENTION",
    "EXIT_OR_TARGET_CONVENTION",
    "INITIAL_STOP",
    "NO_TRADE_GATE",
    "POST_ENTRY_INVALIDATION",
    "SIMULTANEOUS_OR_SAME_BAR_TRIGGER_HANDLING",
    "SINGLE_OPERATING_TIMEFRAME",
    "UNTRIGGERED_OPPOSITE_ORDER_CANCELLATION",
)

# US-market internals referenced by the source that the current China-futures
# 1-minute OHLCV corpus does not own.  Recorded as missing; no proxy invented.
UNAVAILABLE_INPUTS = (
    "ADVANCE_DECLINE_BREADTH",
    "NYSE_TICK",
    "TIKI",
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
        raise ValueError("Raschke NR7 SOURCE_ONLY evidence is unavailable or invalid") from error
    if not isinstance(payload.get("claims"), list) or not isinstance(payload.get("session"), dict):
        raise ValueError("Raschke NR7 SOURCE_ONLY evidence has an invalid structure")
    if len(payload["claims"]) != payload.get("recorded_claim_count"):
        raise ValueError("Raschke NR7 SOURCE_ONLY claim count does not match its evidence")
    return payload


def _source_claims(payload: dict[str, Any]) -> tuple[SourceClaimRef, ...]:
    """SOURCE layer: preserve every admitted claim exactly (id / material / anchor / status)."""
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
            raise ValueError("Raschke NR7 SOURCE_ONLY claim record is invalid") from error
        claims.append(claim)
    if len({claim.claim_id for claim in claims}) != len(claims):
        raise ValueError("Raschke NR7 SOURCE_ONLY claim ids must be unique")
    return tuple(claims)


def _interpretations() -> tuple[InterpretationBranch, ...]:
    """INTERPRETATION layer: preserve pinned facts and unresolved questions.

    No branch is PRIMARY.  The 45-minute and 60-minute early-range variants are
    preserved as two explicit source-supported alternative branches; the generic
    core's ``variant_label``/``source_variant_count`` machinery is contract-level
    and would force every branch to carry one of the two variant labels, which
    would mislabel non-variant branches, so the sub-variant identity is carried
    in ``interpretation_note`` and in the payload's ``early_range_variants``.
    """
    return (
        # --- SOURCE-PINNED facts (EXPLICIT transfer, no PRIMARY) ---
        InterpretationBranch(
            branch_id="SOURCE-PINNED-NR7-DAY-DEFINITION",
            source_claim_ids=("C-RAS-NR7-SEM-001",),
            source_basis=(
                "Source-pinned: an NR7 day is a bar with the narrowest range of "
                "the past seven bars, on the daily bar. The governed daily-bar "
                "boundary for Chinese futures is a project convention, not a "
                "source fact."
            ),
            transfer_status=TransferStatus.EXPLICIT,
        ),
        InterpretationBranch(
            branch_id="SOURCE-PINNED-NR7-LOOKBACK-WINDOW",
            source_claim_ids=("C-RAS-NR7-SEM-002",),
            source_basis=(
                "Source-pinned: the lookback window is seven bars. The exact "
                "inclusive/exclusive window alignment is ambiguous (see "
                "UNRESOLVED-NR7-LOOKBACK-ALIGNMENT)."
            ),
            transfer_status=TransferStatus.EXPLICIT,
        ),
        InterpretationBranch(
            branch_id="SOURCE-PINNED-DAY-AFTER-NR7-SESSION",
            source_claim_ids=("C-RAS-NR7-SEM-003",),
            source_basis=(
                "Source-pinned: the bracket entry session is 'the day after an "
                "NR7 day' (next trading session). The Chinese-futures session "
                "boundary construction is a project convention (see "
                "UNRESOLVED-NEXT-SESSION-BOUNDARY)."
            ),
            transfer_status=TransferStatus.EXPLICIT,
        ),
        InterpretationBranch(
            branch_id="SOURCE-PINNED-EARLY-RANGE-45MIN-VARIANT",
            source_claim_ids=("C-RAS-NR7-SEM-004",),
            source_basis=(
                "Source-permitted alternative: bracketing the first 45 minutes "
                "range worked in the source's own test. Preserved as an explicit "
                "source-supported alternative; no PRIMARY is selected."
            ),
            transfer_status=TransferStatus.EXPLICIT,
            interpretation_note="EARLY_RANGE_VARIANT_45MIN",
        ),
        InterpretationBranch(
            branch_id="SOURCE-PINNED-EARLY-RANGE-60MIN-VARIANT",
            source_claim_ids=("C-RAS-NR7-SEM-004",),
            source_basis=(
                "Source-permitted alternative: bracketing the first hour's range "
                "worked in the source's own test. Preserved as an explicit "
                "source-supported alternative; no PRIMARY is selected."
            ),
            transfer_status=TransferStatus.EXPLICIT,
            interpretation_note="EARLY_RANGE_VARIANT_60MIN",
        ),
        InterpretationBranch(
            branch_id="SOURCE-PINNED-BRACKET-LONG-ENTRY",
            source_claim_ids=("C-RAS-NR7-SEM-005",),
            source_basis=(
                "Source-pinned: the long bracket entry is a buy stop above the "
                "early-morning-range high. The exact tick offset above the high "
                "is NOT_PINNED (see UNRESOLVED-ENTRY-OFFSET-TICK)."
            ),
            transfer_status=TransferStatus.EXPLICIT,
        ),
        InterpretationBranch(
            branch_id="SOURCE-PINNED-BRACKET-SHORT-ENTRY",
            source_claim_ids=("C-RAS-NR7-SEM-006",),
            source_basis=(
                "Source-pinned: the short bracket entry is a sell stop below the "
                "early-morning-range low. The exact tick offset below the low is "
                "NOT_PINNED (see UNRESOLVED-ENTRY-OFFSET-TICK)."
            ),
            transfer_status=TransferStatus.EXPLICIT,
        ),
        InterpretationBranch(
            branch_id="SOURCE-PINNED-ENTRY-ORDER-TYPE-STOP",
            source_claim_ids=("C-RAS-NR7-SEM-007",),
            source_basis=(
                "Source-pinned: 'bracket stops' pins stop-entry orders. The exact "
                "order subtype (stop-market vs stop-limit) and resting/OCO state "
                "machine are not stated by the source."
            ),
            transfer_status=TransferStatus.EXPLICIT,
        ),
        InterpretationBranch(
            branch_id="SOURCE-PINNED-TREND-DAY-DEFINITION",
            source_claim_ids=("C-RAS-NR7-SEM-013",),
            source_basis=(
                "Source-pinned, price-based: a trend day opens on one end of its "
                "range, closes on the opposite end, has range expansion, and "
                "makes a steady pattern of higher highs and higher lows (or vice "
                "versa). Numerical thresholds for 'range expansion' / 'steady' "
                "are not quantified by the source."
            ),
            transfer_status=TransferStatus.EXPLICIT,
        ),
        InterpretationBranch(
            branch_id="SOURCE-PINNED-CONFIRMATION-COMPONENTS",
            source_claim_ids=("C-RAS-NR7-SEM-014", "C-RAS-NR7-SEM-015"),
            source_basis=(
                "Source-pinned, qualitative: trend-day confirmation includes a "
                "very large 15-minute opening bar (Crabel), a significant volume "
                "increase in the first 15 minutes relative to the past two weeks, "
                "leadership names, and a trendiness window. Thresholds are left "
                "to the trader; breadth is a separate unavailable-input field."
            ),
            transfer_status=TransferStatus.EXPLICIT,
        ),
        InterpretationBranch(
            branch_id="SOURCE-PINNED-BREADTH-TICK-CONFIRMATION-HANDICAP",
            source_claim_ids=("C-RAS-NR7-SEM-016",),
            source_basis=(
                "Source-pinned (concept): the source uses NYSE TICK / "
                "advancing-minus-declining breadth as a confirmation handicap, "
                "NOT the NR7 bracket entry trigger. This surface is "
                "NOT_OBSERVABLE_WITH_CURRENT_DATA; no OHLCV proxy is authorized."
            ),
            transfer_status=TransferStatus.EXPLICIT,
        ),
        InterpretationBranch(
            branch_id="SOURCE-PINNED-EXIT-MANAGEMENT-CONCEPT",
            source_claim_ids=("C-RAS-NR7-SEM-017", "C-RAS-NR7-SEM-018"),
            source_basis=(
                "Source-pinned, qualitative: ride the trend day (hold to end of "
                "day / add during the day / maybe hold part overnight); get out "
                "on the first reaction or pause when price gives back more than "
                "it should; take at least half off at an uncertain price "
                "objective. No numeric target or deterministic end-of-session "
                "rule is pinned."
            ),
            transfer_status=TransferStatus.EXPLICIT,
        ),
        InterpretationBranch(
            branch_id="SOURCE-PINNED-NO-TRADE-FAILURE-CONTEXT",
            source_claim_ids=("C-RAS-NR7-SEM-019", "C-RAS-NR7-SEM-020"),
            source_basis=(
                "Source-pinned, qualitative: do not guess breakout direction "
                "(wrong ~90% of the time); do not buy in the middle of a trading "
                "range; without volume/breadth improvement the market is likely "
                "range-bound; flags fail at volatility extremes; Eaton Corp "
                "no-trade example. No deterministic no-trade gate is pinned."
            ),
            transfer_status=TransferStatus.EXPLICIT,
        ),
        InterpretationBranch(
            branch_id="SOURCE-PINNED-TIMEFRAME-SCOPE",
            source_claim_ids=("C-RAS-NR7-SEM-021",),
            source_basis=(
                "Source-pinned: the family is explicitly multi-timeframe (daily "
                "setup, intraday entry, 15-minute confirmation, hourly "
                "management). No single operating timeframe is pinned for the "
                "whole loop."
            ),
            transfer_status=TransferStatus.EXPLICIT,
        ),
        InterpretationBranch(
            branch_id="SOURCE-PINNED-INSTRUMENT-SCOPE",
            source_claim_ids=("C-RAS-NR7-SEM-022",),
            source_basis=(
                "Source-pinned: SOURCE_INSTRUMENT_SCOPE is US equity index "
                "futures + US equities + commodity futures (NR7 concept); the "
                "exact bracket practice is stated in an index-futures context. "
                "SOURCE_SUPPORTS_CROSS_MARKET_TRANSFER=UNKNOWN."
            ),
            transfer_status=TransferStatus.EXPLICIT,
        ),
        # --- PROJECT/AI INFERRED transfer (explicitly labeled, never source fact) ---
        InterpretationBranch(
            branch_id="PROJECT-INFERRED-CHINESE-FUTURES-TRANSFER",
            source_claim_ids=("C-RAS-NR7-SEM-023",),
            source_basis=(
                "INFERRED_PROJECT_TRANSFER: transferring the exact day-after-NR7 "
                "early-morning-range bracket practice to cu/al/ni/au/ag/rb is a "
                "project hypothesis, NOT an explicit source claim. "
                "SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN."
            ),
            transfer_status=TransferStatus.INFERRED,
        ),
        # --- UNRESOLVED questions (transfer UNKNOWN, no PRIMARY) ---
        InterpretationBranch(
            branch_id="UNRESOLVED-NR7-LOOKBACK-ALIGNMENT",
            source_claim_ids=("C-RAS-NR7-SEM-002",),
            source_basis=(
                "Inclusive vs exclusive seven-bar window alignment is ambiguous "
                "between the two accepted source statements; no project window "
                "convention is chosen here."
            ),
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-NEXT-SESSION-BOUNDARY",
            source_claim_ids=("C-RAS-NR7-SEM-003",),
            source_basis=(
                "The Chinese-futures session boundary construction (night session "
                "vs calendar day; which session 'early morning' maps to) is a "
                "governed-metadata project convention, not source-defined."
            ),
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-EARLY-RANGE-PRIMARY",
            source_claim_ids=("C-RAS-NR7-SEM-004",),
            source_basis=(
                "The 45-minute and 60-minute early-range formulations are both "
                "SOURCE_PERMITTED; the accepted evidence justifies no unique "
                "PRIMARY. Neither variant is outcome-selected."
            ),
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-ENTRY-OFFSET-TICK",
            source_claim_ids=("C-RAS-NR7-SEM-008",),
            source_basis=(
                "No source offset/tick convention is pinned for placing the "
                "bracket stops relative to the early-morning-range high/low. Any "
                "offset is a clearly labeled project convention."
            ),
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-OPPOSITE-ORDER-CANCELLATION",
            source_claim_ids=("C-RAS-NR7-SEM-009",),
            source_basis=(
                "No source statement defines what happens to the untriggered "
                "opposite bracket order after one side fills; OCO / cancel-on-fill "
                "is a project convention, not a source claim."
            ),
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-SAME-BAR-TRIGGER-HANDLING",
            source_claim_ids=("C-RAS-NR7-SEM-010",),
            source_basis=(
                "No source statement defines same-bar / simultaneous handling "
                "when a bar trades through both bracket sides."
            ),
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-POST-ENTRY-INVALIDATION",
            source_claim_ids=("C-RAS-NR7-SEM-011",),
            source_basis=(
                "No source evidence establishes a post-entry invalidation boundary "
                "for the day-after-NR7 early-morning-range bracket family "
                "(integration correction IC-1: the opposite bracket side is an "
                "ENTRY placement, not an established source stop/invalidation). "
                "A project boundary would be invented."
            ),
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-INITIAL-STOP",
            source_claim_ids=("C-RAS-NR7-SEM-012",),
            source_basis=(
                "No source-pinned initial protective stop exists for the "
                "day-after-NR7 early-morning-range bracket family "
                "(INITIAL_STOP=NOT_PINNED). A numeric initial stop would be "
                "invented. No ATR / opposite-range / percentage / fixed-tick / "
                "time stop rule is imported from any other family."
            ),
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-CONFIRMATION-THRESHOLDS",
            source_claim_ids=("C-RAS-NR7-SEM-014",),
            source_basis=(
                "'Very large' 15-minute bar, 'significant increase' in volume and "
                "the trendiness window are not numerically pinned; the source "
                "explicitly leaves the 'big bar' threshold to the trader."
            ),
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-EXIT-TARGET-CONVENTION",
            source_claim_ids=("C-RAS-NR7-SEM-017",),
            source_basis=(
                "'Gives back more than it should', 'price objective' and 'big "
                "target' are qualitative; no unique numeric target / give-back "
                "convention is pinned."
            ),
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-END-OF-SESSION-RULE",
            source_claim_ids=("C-RAS-NR7-SEM-018",),
            source_basis=(
                "Hold all / add during the day / maybe hold part overnight are "
                "qualitative options, not a deterministic end-of-session rule."
            ),
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-NO-TRADE-GATE",
            source_claim_ids=("C-RAS-NR7-SEM-019",),
            source_basis=(
                "'Middle of a trading range', 'no improvement' and 'scalp mode' "
                "are qualitative; no deterministic no-trade gate is pinned, and "
                "the breadth component is unavailable."
            ),
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-MULTI-TIMEFRAME-PRIMARY",
            source_claim_ids=("C-RAS-NR7-SEM-021",),
            source_basis=(
                "The multi-timeframe source does not pin one machine PRIMARY "
                "operating timeframe for the whole loop."
            ),
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-CROSS-MARKET-TRANSFER",
            source_claim_ids=("C-RAS-NR7-SEM-022",),
            source_basis=(
                "SOURCE_SUPPORTS_CROSS_MARKET_TRANSFER=UNKNOWN; no explicit "
                "source statement authorizes transferring the exact bracket "
                "trade across asset classes."
            ),
            transfer_status=TransferStatus.UNKNOWN,
        ),
        InterpretationBranch(
            branch_id="UNRESOLVED-BREADTH-TICK-UNAVAILABLE",
            source_claim_ids=("C-RAS-NR7-SEM-016",),
            source_basis=(
                "NYSE TICK / advance-decline breadth / TIKI are US market "
                "internals NOT owned by the Chinese-futures corpus. Recorded as "
                "NOT_OBSERVABLE_WITH_CURRENT_DATA; no price/volume/ADX/RSI/MACD/"
                "open-interest proxy is authorized."
            ),
            transfer_status=TransferStatus.UNKNOWN,
        ),
    )


def _observation_surfaces() -> tuple[ObservationSurface, ...]:
    """Required observation surfaces and point-in-time observability.

    Breadth/TICK is a non-required source confirmation handicap (not the bracket
    entry trigger) and is recorded as NOT_OBSERVABLE_WITH_CURRENT_DATA.
    """
    return (
        ObservationSurface(
            surface_id="NR7_DAILY_BAR_SETUP",
            required=True,
            observability_status=ObservabilityStatus.OBSERVABLE_NOW,
        ),
        ObservationSurface(
            surface_id="NEXT_SESSION_DAILY_BAR_BOUNDARY",
            required=True,
            observability_status=ObservabilityStatus.PARTIALLY_OBSERVABLE,
            missing_inputs=("chinese_futures_daily_bar_boundary_convention",),
        ),
        ObservationSurface(
            surface_id="EARLY_MORNING_RANGE",
            required=True,
            observability_status=ObservabilityStatus.OBSERVABLE_NOW,
        ),
        ObservationSurface(
            surface_id="BRACKET_ENTRY_ORDER_SEMANTICS",
            required=True,
            observability_status=ObservabilityStatus.PARTIALLY_OBSERVABLE,
            missing_inputs=(
                "entry_offset_or_tick_convention",
                "oco_cancellation_semantics",
                "order_subtype",
                "same_bar_trigger_ordering",
            ),
        ),
        ObservationSurface(
            surface_id="POST_ENTRY_RISK_LOOP",
            required=True,
            observability_status=ObservabilityStatus.PARTIALLY_OBSERVABLE,
            missing_inputs=(
                "initial_stop",
                "post_entry_invalidation",
            ),
        ),
        ObservationSurface(
            surface_id="TREND_DAY_PRICE_SURFACE",
            required=True,
            observability_status=ObservabilityStatus.OBSERVABLE_NOW,
        ),
        ObservationSurface(
            surface_id="TREND_DAY_CONFIRMATION",
            required=True,
            observability_status=ObservabilityStatus.PARTIALLY_OBSERVABLE,
            missing_inputs=("confirmation_thresholds",),
        ),
        ObservationSurface(
            surface_id="BREADTH_TICK_HANDICAP",
            required=False,
            observability_status=ObservabilityStatus.NOT_OBSERVABLE_WITH_CURRENT_DATA,
            missing_inputs=UNAVAILABLE_INPUTS,
        ),
        ObservationSurface(
            surface_id="EXIT_AND_END_OF_SESSION",
            required=True,
            observability_status=ObservabilityStatus.PARTIALLY_OBSERVABLE,
            missing_inputs=(
                "end_of_session_rule",
                "exit_or_target_convention",
            ),
        ),
        ObservationSurface(
            surface_id="NO_TRADE_AND_FAILURE_CONTEXT",
            required=True,
            observability_status=ObservabilityStatus.PARTIALLY_OBSERVABLE,
            missing_inputs=("no_trade_gate_thresholds",),
        ),
        ObservationSurface(
            surface_id="MULTI_TIMEFRAME_SCOPE",
            required=True,
            observability_status=ObservabilityStatus.OBSERVABLE_NOW,
        ),
        ObservationSurface(
            surface_id="INSTRUMENT_SCOPE",
            required=True,
            observability_status=ObservabilityStatus.PARTIALLY_OBSERVABLE,
            missing_inputs=("cross_market_transfer_justification",),
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
    if any(
        not isinstance(session.get(field), str) or not session[field]
        for field in required_session_fields
    ):
        raise ValueError("Raschke NR7 SOURCE_ONLY session identity is incomplete")
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
            "The accepted SOURCE_ONLY evidence does not pin the post-entry risk "
            "loop (INITIAL_STOP=NOT_PINNED; POST_ENTRY_INVALIDATION=NOT_PINNED, "
            "integration correction IC-1), does not justify a unique "
            "early-morning-range PRIMARY (45-minute and 60-minute are both "
            "SOURCE_PERMITTED), and leaves order-mechanics, exit/target, "
            "no-trade, and Chinese-futures session-boundary conventions "
            "unresolved. No implementation convention is PRIMARY; no Holy Grail "
            "stop semantics are imported."
        ),
        primary_required=True,
        source_variant_count=1,
        observation_surfaces=_observation_surfaces(),
        unavailable_inputs=UNAVAILABLE_INPUTS,
        instrument_scope=("ag", "al", "au", "cu", "ni", "rb"),
        timeframe_scope=("15MIN", "60MIN", "DAILY", "INTRADAY"),
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
        "artifact": "RASCHKE_NR7_PLAYBOOK_CONTRACT_DRAFT_V0_1",
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
        "claim_semantics": [
            {
                "claim_id": record["claim_id"],
                "source_id": record["material_id"],
                "source_anchor": record["source_anchor"],
                "claim_status": record["claim_status"],
                "claim_category": record["claim_category"],
                "semantic_field": record["semantic_field"],
                "semantic_classification": record["semantic_classification"],
                "observability_compatibility": record["observability_compatibility"],
                "observability_missing_inputs": record["observability_missing_inputs"],
                "lineage_id": record["lineage_id"],
                "primary_branch_status": record["primary_branch_status"],
                "machine_operationalization_status": record["machine_operationalization_status"],
                "source_excerpt_short_or_paraphrase": record["source_excerpt_short_or_paraphrase"],
                "source_context_note": record["source_context_note"],
            }
            for record in evidence["claims"]
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
        "source_variant_count": contract.source_variant_count,
        "early_range_variants": list(EARLY_RANGE_VARIANTS),
        "early_range_primary_status": "NONE_SOURCE_JUSTIFIED",
        "primary_blocker": (
            "SOURCE_POST_ENTRY_RISK_SEMANTICS_NOT_PINNED "
            "(INITIAL_STOP=NOT_PINNED; POST_ENTRY_INVALIDATION=NOT_PINNED)"
        ),
        "source_supports_current_project_products": "UNKNOWN",
        "playbook_semantically_draftable": "NO",
        "machine_operationalization": None,
        "machine_readiness": validation.readiness.value,
        "machine_readiness_blockers": list(validation.blockers),
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
        raise SystemExit("Raschke NR7 draft unexpectedly became machine ready")
    OUTPUT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

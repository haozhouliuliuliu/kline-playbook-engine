"""Build the Holy Grail V0.4 Playbook Contract (machine-ready).

V0.4 is the machine operationalization revision of the Holy Grail pullback
playbook.  It preserves the immutable V0.3 source-claim corpus / provenance
verbatim (SOURCE CLAIM layer) while closing the four operationalization
prerequisites with the binding Owner approval of 2026-08-21
(``docs/evidence/HOLY_GRAIL_MACHINE_OPERATIONALIZATION_OWNER_APPROVAL_2026-08-21.md``):

- HOLY_GRAIL_BASE_TO_MACHINE_INTERVAL   = 1_MINUTE        (PROJECT_INFERRED)
- HOLY_GRAIL_ADX_RISING_WINDOW          = 1_STEP          (PROJECT_INFERRED_VERSIONED_NON_OUTCOME)
- HOLY_GRAIL_SWING_CONFIRMATION_COUNTS  = L1_R1           (PROJECT_INFERRED_VERSIONED_NON_OUTCOME)
- HOLY_GRAIL_TRAILING_STOP_MACHINE_DEFINITION = SWING_BASED_TRAILING (PROJECT_INFERRED)
- TRAILING_CLASSIFICATION               = PROJECT_INFERRED

Every Owner-approved machine convention is a PROJECT INTERPRETATION (INFERRED)
branch, never a source claim.  V0.4 additionally resolves claim-level PRIMARY for
all 27 source claims (Protocol v1.0 section 2), installs the MACHINE layer
(``src/holy_grail_machine.py`` with real byte identity binding), and therefore
passes ``validate_contract`` as MACHINE_READY.

This builder performs no candidate outcome access, no StrategyIdentity creation,
no outcome-test registration, and no validation / final-holdout / shadow access.
"""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from src.playbook_contract import (
    AmbiguityStatus,
    ClaimStatus,
    InterpretationBranch,
    MachineOperationalization,
    ObservationSurface,
    ObservabilityStatus,
    PlaybookContract,
    SourceClaimRef,
    TransferStatus,
    parameter_identity,
    validate_contract,
)
from src.strategy_evidence import TypedParameter
from src.holy_grail_machine import (
    HOLY_GRAIL_MACHINE_FEATURE_VERSION,
    MACHINE_IMPLEMENTATION_BINDING,
    HolyGrailMachineParameters,
)
from src.stop_order_execution import SUPPORTED_TRIGGER_MODEL_VERSION
from src.technical_features import FEATURE_IMPLEMENTATION_BINDING


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
    / "RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_4.json"
)
OWNER_APPROVAL_EVIDENCE = (
    "docs/evidence/HOLY_GRAIL_MACHINE_OPERATIONALIZATION_OWNER_APPROVAL_2026-08-21.md"
)

FAMILY_ID = "RASCHKE_HOLY_GRAIL_PULLBACK"
CONTRACT_ID = "PC-RASCHKE-HOLY-GRAIL-PULLBACK-DRAFT-V0-4"
PARENT_CONTRACT_ID = "PC-RASCHKE-HOLY-GRAIL-PULLBACK-DRAFT-V0-3"
RESEARCH_LINEAGE_ID = "L-RAS-HOLYGRAIL"
SCHEMA_VERSION = "0.4"
CONTRACT_VERSION = "0.4.0"
CREATED_AT = "2026-08-21T00:00:00Z"
SOURCE_SCOPE = "US_EQUITIES_AND_US_INDEX"
DATA_EXPOSURE_HISTORY_REFERENCE = (
    "docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_HOLY_GRAIL_V0_1.json"
)
BASE_TIME_INTERVAL = "1MIN"


def _canonical_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


# Binding Owner-approved decisions (2026-08-21).  Every value is a PROJECT
# INFERRED machine convention; none is a source claim.
OWNER_APPROVED_DECISIONS: dict[str, dict[str, str]] = {
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
        "ADX_RISING_WINDOW": "1_STEP",
        "ADX_RISING_WINDOW_CLASSIFICATION": "PROJECT_INFERRED_VERSIONED_NON_OUTCOME",
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
        "BASE_TO_MACHINE_INTERVAL": "1_MINUTE",
        "BASE_TO_MACHINE_INTERVAL_CLASSIFICATION": "PROJECT_INFERRED",
    },
    "SWING_LOW_HIGH": {
        "SWING_DEFINITION": "FRACTAL_PIVOT_EXPLICIT_CONFIRMATION",
        "RIGHT_SIDE_CONFIRMATION_REQUIRED": "YES",
        "SAME_BAR_AVAILABILITY": "NO",
        "SHORT_SIDE": "MIRROR_SWING_HIGH",
        "SWING_CONFIRMATION_COUNTS": "L1_R1",
        "SWING_CONFIRMATION_COUNTS_CLASSIFICATION": "PROJECT_INFERRED_VERSIONED_NON_OUTCOME",
    },
    "TRAILING_STOP": {
        "TRAILING_STOP_MACHINE_DEFINITION": "SWING_BASED_TRAILING",
        "TRAILING_CLASSIFICATION": "PROJECT_INFERRED",
        "MONOTONIC_TIGHTEN_ONLY": "YES",
        "OUTCOME_TUNING_FOR_TRAILING": "FORBIDDEN",
    },
    "EXIT_ON_PUSH_TO_NEW_HIGHS": {
        "EXIT_ON_PUSH_TO_NEW_HIGHS": "OPTIONAL_VERSIONED_VARIANT",
        "PRIMARY_EXIT_REPLACED": "NO",
        "OUTCOME_RESCUE": "FORBIDDEN",
    },
    "OWNER_APPROVAL": {
        "OWNER_APPROVAL_EVIDENCE": OWNER_APPROVAL_EVIDENCE,
        "CANDIDATE_OUTCOME_USED": "NO",
        "VALIDATION_ACCESS": "LOCKED_BY_PROJECT_POLICY",
        "HISTORICAL_FINAL_HOLDOUT_ACCESS": "LOCKED",
    },
}

OPEN_PREREQUISITES: dict[str, str] = {}

UNRESOLVED_MACHINE_DEFINITIONS: tuple[str, ...] = ()

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


def _branch(
    branch_id: str,
    source_claim_ids: tuple[str, ...],
    source_basis: str,
    transfer: TransferStatus,
    primary: bool,
) -> InterpretationBranch:
    return InterpretationBranch(
        branch_id=branch_id,
        source_claim_ids=source_claim_ids,
        source_basis=source_basis,
        transfer_status=transfer,
        primary_selected=primary,
    )


def _interpretations() -> tuple[InterpretationBranch, ...]:
    """Full branch set covering all 27 source claims with exactly one PRIMARY
    branch per claim (Protocol v1.0 section 2 / Package C P-01)."""
    return (
        # ---- SOURCE-pinned branches (EXPLICIT) -------------------------------
        _branch(
            "SOURCE-PINNED-ADX-EMA-CONCEPTS",
            ("C-RAS-HG-SEM-002", "C-RAS-HG-SEM-003", "C-RAS-HG-SEM-004",
             "C-RAS-HG-SEM-005", "C-RAS-HG-SEM-006"),
            "Source-pinned facts only: 14-period ADX, initially greater than 30 and rising, "
            "and the 20-period exponential moving average concept.",
            TransferStatus.EXPLICIT,
            primary=False,
        ),
        _branch(
            "SOURCE-PINNED-ENTRY-RISK-EXIT-CONCEPTS",
            ("C-RAS-HG-SEM-009", "C-RAS-HG-SEM-010", "C-RAS-HG-SEM-013",
             "C-RAS-HG-SEM-015", "C-RAS-HG-SEM-016", "C-RAS-HG-SEM-017",
             "C-RAS-HG-SEM-019"),
            "Source-pinned concepts only: EMA pullback/touch, buy stop above the previous-bar "
            "high, protective stop at the newly formed swing low once filled, trailing stops, "
            "and exit on a push to new highs.  Non-primary overview branch; each claim's "
            "PRIMARY is resolved by the specific machine convention branch.",
            TransferStatus.EXPLICIT,
            primary=False,
        ),
        _branch(
            "SOURCE-PINNED-LONG-RULE-CONCEPT",
            ("C-RAS-HG-SEM-013",),
            "Source-pinned complete 4-step long rule (C-RAS-HG-SEM-013): trend/ADX context, "
            "pullback to the 20-period EMA, buy-stop entry above the previous-bar high, "
            "protective sell stop at the newly formed swing low, trail as profits grow.",
            TransferStatus.EXPLICIT,
            primary=True,
        ),
        _branch(
            "SOURCE-PINNED-MULTI-TIMEFRAME-CONCEPT",
            ("C-RAS-HG-SEM-024",),
            "The source is explicitly multi-timeframe, including base, 30, 60 and 120 minute "
            "contexts; it does not pin a single project PRIMARY timeframe.",
            TransferStatus.EXPLICIT,
            primary=False,
        ),
        _branch(
            "SOURCE-PINNED-TREND-CONTEXT-CONCEPT",
            ("C-RAS-HG-SEM-001",),
            "Source-pinned trend context: the setup follows an extended trading range breakout "
            "into new momentum highs, with the 14-period ADX>30-and-rising filter as the explicit "
            "numeric component and the range/momentum-highs structure qualitative.",
            TransferStatus.EXPLICIT,
            primary=True,
        ),
        _branch(
            "SOURCE-PINNED-PULLBACK-TO-EMA-CONCEPT",
            ("C-RAS-HG-SEM-008",),
            "Source-pinned pullback concept: price retraces to the 20-period exponential moving "
            "average; the pullback target (EMA) is explicit while the leg/depth/duration is not "
            "numerically pinned.",
            TransferStatus.EXPLICIT,
            primary=True,
        ),
        _branch(
            "SOURCE-PINNED-ENTRY-ORDER-TYPE-CONCEPT",
            ("C-RAS-HG-SEM-011",),
            "Source-pinned entry order type: buy stop for the long (sell stop for the short); "
            "the stop-market vs stop-limit subtype is an INFERRED operational detail.",
            TransferStatus.EXPLICIT,
            primary=True,
        ),
        _branch(
            "SOURCE-PINNED-ENTRY-OFFSET-ABOVE-PREVIOUS-HIGH",
            ("C-RAS-HG-SEM-012",),
            "Source-pinned entry reference: buy stop above the high of the previous bar.  The "
            "exact offset is INFERRED (1 tick, strict above).",
            TransferStatus.EXPLICIT,
            primary=True,
        ),
        _branch(
            "SOURCE-PINNED-SHORT-MIRROR-CONCEPT",
            ("C-RAS-HG-SEM-014",),
            "Source-pinned short rule: '(sells reversed)' mirrors the 4-step buy rules; the "
            "short operationalization is the mirror image of the long side.",
            TransferStatus.EXPLICIT,
            primary=True,
        ),
        _branch(
            "SOURCE-PINNED-PROFIT-TARGET-CONCEPT",
            ("C-RAS-HG-SEM-018",),
            "Source-pinned profit-target concept: take at least half off at a price objective "
            "when continuation is uncertain; no numeric target is pinned (qualitative).",
            TransferStatus.EXPLICIT,
            primary=True,
        ),
        _branch(
            "SOURCE-PINNED-NO-TRADE-CONCEPT",
            ("C-RAS-HG-SEM-022",),
            "Source-pinned no-trade constraints: do not buy in the middle of a trading range; "
            "avoid ADX below 20 and declining; do not fade ADX above 32 and rising; do not "
            "guess a breakout.  Operational boundaries (range/slope) are INFERRED.",
            TransferStatus.EXPLICIT,
            primary=True,
        ),
        _branch(
            "SOURCE-PINNED-FAILURE-CONCEPT",
            ("C-RAS-HG-SEM-023",),
            "Source-pinned failure/counterexample: the Eaton Corp no-trade/failure case and the "
            "guess-breakout failure statement; source-quality limitation recorded, not "
            "manufactured.",
            TransferStatus.EXPLICIT,
            primary=True,
        ),
        _branch(
            "SOURCE-PINNED-INSTRUMENT-SCOPE-CONCEPT",
            ("C-RAS-HG-SEM-025",),
            "Source-pinned instrument scope: US equities and US index context; 'on all my "
            "markets' is lineage context, not explicit commodity-futures support.",
            TransferStatus.EXPLICIT,
            primary=True,
        ),
        _branch(
            "SOURCE-PINNED-NO-TIME-EXIT",
            ("C-RAS-HG-SEM-020",),
            "Source silence: no time-based exit (end-of-session / N-bar / end-of-day) is stated "
            "for the Holy Grail pullback family; no time-exit rule is invented.",
            TransferStatus.UNKNOWN,
            primary=True,
        ),
        _branch(
            "SOURCE-PINNED-NO-REENTRY",
            ("C-RAS-HG-SEM-021",),
            "Source silence: no explicit re-entry rule exists; the multi-timeframe sequence is "
            "context, not a re-entry rule, and none is invented.",
            TransferStatus.UNKNOWN,
            primary=True,
        ),
        _branch(
            "SOURCE-PINNED-COMMODITY-SCOPE-UNKNOWN",
            ("C-RAS-HG-SEM-026",),
            "Source silence: no explicit commodity-futures support statement for the Holy Grail "
            "family; absence of support is not evidence of failure.",
            TransferStatus.UNKNOWN,
            primary=True,
        ),
        _branch(
            "PROJECT-INFERRED-CURRENT-PRODUCT-TRANSFER",
            ("C-RAS-HG-SEM-027",),
            "Project INFERRED transfer: operationalizing the Holy Grail pullback on "
            "cu/al/ni/au/ag/rb is a separately labeled project hypothesis; it never inherits "
            "source authority automatically.",
            TransferStatus.INFERRED,
            primary=True,
        ),
        # ---- Owner-approved machine conventions (INFERRED) --------------------
        _branch(
            "OWNER-APPROVED-EMA-TOUCH-CONVENTION",
            ("C-RAS-HG-SEM-005", "C-RAS-HG-SEM-006", "C-RAS-HG-SEM-007",
             "C-RAS-HG-SEM-009"),
            "Owner-approved EMA touch convention (FGH-GATE-01 + 2026-08-21 ratification), "
            "project INFERRED machine convention: EMA_PERIOD=20; EMA_PRICE_BASIS="
            "PROJECT_INFERRED_CLOSE (not a source claim); EMA_REFERENCE="
            "PRIOR_COMPLETED_BAR_AVAILABLE; TOUCH_RULE=BAR_LOW_LE_EMA_PRIOR_LE_BAR_HIGH; "
            "CURRENT_BAR_CLOSE_LOOKAHEAD=FORBIDDEN.",
            TransferStatus.INFERRED,
            primary=True,
        ),
        _branch(
            "OWNER-APPROVED-ADX-PRE-PULLBACK-CONTEXT",
            ("C-RAS-HG-SEM-002", "C-RAS-HG-SEM-003", "C-RAS-HG-SEM-004"),
            "Owner-approved ADX pre-pullback context (FGH-GATE-02 + 2026-08-21 binding "
            "1_STEP): source period/threshold preserved (ADX_PERIOD=14; ADX_THRESHOLD=>30); "
            "ADX_CONTEXT=INITIAL_PRE_PULLBACK; TOUCH_BAR_RISING_REQUIRED=NO; "
            "ADX_RISING_WINDOW=1_STEP (ADX[t]>ADX[t-1] at the initial pre-pullback context "
            "bar); OLD_TOUCH_BAR_ONE_STEP_RULE=NOT_AUTHORITY.",
            TransferStatus.INFERRED,
            primary=True,
        ),
        _branch(
            "OWNER-APPROVED-NUMERIC-POLICY",
            ("C-RAS-HG-SEM-002", "C-RAS-HG-SEM-005"),
            "Owner-approved numeric policy (FGH-GATE-03), project INFERRED machine fact: "
            "EMA_SEED=SMA; ADX_INITIALIZATION=WILDER_SMA_DX; ARITHMETIC=DECIMAL; "
            "QUANTIZATION=6DP_ROUND_HALF_UP; NUMERIC_POLICY=VERSIONED_IDENTITY_BOUND.",
            TransferStatus.INFERRED,
            primary=False,
        ),
        _branch(
            "OWNER-APPROVED-SAME-BAR-TOUCH-ENTRY",
            ("C-RAS-HG-SEM-010",),
            "Owner-approved same-bar touch->entry (FGH-GATE-04): SAME_BAR_TOUCH_ENTRY="
            "AMBIGUOUS_INTRABAR_SEQUENCE; FAIL_CLOSED=YES.  At 1-minute resolution, if the EMA "
            "touch and the entry-stop threshold are reached inside the same bar and their "
            "ordering is not observable, fail closed.",
            TransferStatus.INFERRED,
            primary=True,
        ),
        _branch(
            "OWNER-APPROVED-FILL-PROTECTIVE-STOP-CHRONOLOGY",
            ("C-RAS-HG-SEM-016",),
            "Owner-approved fill->protective-stop chronology (FGH-GATE-05): CHRONOLOGY="
            "COMPLETED_BAR_AVAILABILITY_CONSERVATIVE; EXCHANGE_RESTING_CLAIM=NO; "
            "SAME_BAR_FILL_STOP=AMBIGUOUS_INTRABAR_SEQUENCE; NEXT_BAR_ONLY_STOP_ACTIVATION_"
            "DEFAULT=REJECTED; INTRABAR_ORDERING=NOT_OBSERVABLE_AT_1M.",
            TransferStatus.INFERRED,
            primary=True,
        ),
        _branch(
            "OWNER-APPROVED-SWING-LOW-DEFINITION",
            ("C-RAS-HG-SEM-015",),
            "Owner-approved swing low/high definition (2026-08-20 + 2026-08-21 binding "
            "L1_R1), project INFERRED machine convention: SWING_DEFINITION="
            "FRACTAL_PIVOT_EXPLICIT_CONFIRMATION; RIGHT_SIDE_CONFIRMATION_REQUIRED=YES; "
            "SAME_BAR_AVAILABILITY=NO; SHORT_SIDE=MIRROR_SWING_HIGH; "
            "SWING_CONFIRMATION_COUNTS=L1_R1 (3-bar fractal: low[t]<low[t-1] and "
            "low[t]<low[t+1]; pivot t confirmed only after bar t+1 completes).",
            TransferStatus.INFERRED,
            primary=True,
        ),
        _branch(
            "OWNER-APPROVED-SWING-BASED-TRAILING",
            ("C-RAS-HG-SEM-017",),
            "Owner-approved swing-based trailing (2026-08-21 binding), project INFERRED "
            "machine convention: TRAILING_STOP_MACHINE_DEFINITION=SWING_BASED_TRAILING; "
            "TRAILING_CLASSIFICATION=PROJECT_INFERRED; MONOTONIC_TIGHTEN_ONLY=YES.  Long "
            "raises the protective stop to each newly confirmed swing low; short lowers to "
            "each newly confirmed swing high; a worse pivot is ignored and no stop is ever "
            "loosened.  This splices the source's initial-stop statement with 'trail stops as "
            "profits grow'; it is NOT a source claim.",
            TransferStatus.INFERRED,
            primary=True,
        ),
        _branch(
            "OWNER-APPROVED-TIMEFRAME-BASE-BRANCH",
            ("C-RAS-HG-SEM-024",),
            "Owner-approved timeframe branch (FGH-GATE-06 + 2026-08-21 binding 1_MINUTE), "
            "project INFERRED machine convention: PRIMARY_TIMEFRAME_BRANCH=BASE; "
            "SOURCE_ALTERNATIVES=30MIN,60MIN,120MIN (source alternatives preserved, not "
            "promoted to PRIMARY); BASE_TO_MACHINE_INTERVAL=1_MINUTE; "
            "BASE_TO_MACHINE_INTERVAL_CLASSIFICATION=PROJECT_INFERRED.",
            TransferStatus.INFERRED,
            primary=True,
        ),
        _branch(
            "OWNER-APPROVED-EXIT-NEW-HIGHS-OPTIONAL",
            ("C-RAS-HG-SEM-019",),
            "Owner-approved exit decision (2026-08-20): EXIT_ON_PUSH_TO_NEW_HIGHS="
            "OPTIONAL_VERSIONED_VARIANT; PRIMARY_EXIT_REPLACED=NO; OUTCOME_RESCUE=FORBIDDEN.  "
            "The later source wording about exit on a push to new highs is an optional "
            "versioned variant, not the Holy Grail PRIMARY exit.",
            TransferStatus.INFERRED,
            primary=True,
        ),
    )


def _observation_surfaces() -> tuple[ObservationSurface, ...]:
    """All required surfaces are fully observable under the completed-bar
    conservative model and the Owner-approved L1_R1 / swing-trailing machine
    conventions."""
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
            observability_status=ObservabilityStatus.OBSERVABLE_NOW,
        ),
        ObservationSurface(
            surface_id="SWING_LOW_CONFIRMATION",
            required=True,
            observability_status=ObservabilityStatus.OBSERVABLE_NOW,
        ),
        ObservationSurface(
            surface_id="TRAILING_STOP_MACHINE_DEFINITION",
            required=True,
            observability_status=ObservabilityStatus.OBSERVABLE_NOW,
        ),
    )


def strategy_parameters() -> tuple[TypedParameter, ...]:
    """Expose V0.4's fixed machine conventions at StrategyIdentity granularity."""
    values = HolyGrailMachineParameters()
    return (
        TypedParameter("adx_initialization", "str", values.adx_initialization),
        TypedParameter("adx_period", "int", values.adx_period),
        TypedParameter("adx_rising_window", "str", values.adx_rising_window),
        TypedParameter("adx_threshold", "str", str(values.adx_threshold)),
        TypedParameter("base_timeframe", "str", values.base_timeframe),
        TypedParameter("ema_period", "int", values.ema_period),
        TypedParameter("ema_price_field", "str", values.ema_price_field),
        TypedParameter("ema_seed", "str", values.ema_seed),
        TypedParameter("entry_offset_ticks", "int", values.entry_offset_ticks),
        TypedParameter("monotonic_tighten_only", "bool", values.monotonic_tighten_only),
        TypedParameter("numeric_arithmetic", "str", values.numeric_arithmetic),
        TypedParameter("numeric_quantization", "str", values.numeric_quantization),
        TypedParameter("swing_left_count", "int", values.swing_left_count),
        TypedParameter("swing_right_count", "int", values.swing_right_count),
        TypedParameter("trailing_classification", "str", values.trailing_classification),
        TypedParameter("trailing_stop", "str", values.trailing_stop),
    )


def _machine_operationalization() -> MachineOperationalization:
    """Real MACHINE layer identity binding for ``src/holy_grail_machine.py``."""
    required_feature_versions = tuple(
        sorted(
            {
                FEATURE_IMPLEMENTATION_BINDING.identity_id,
                HOLY_GRAIL_MACHINE_FEATURE_VERSION,
            }
        )
    )
    environment_hash = _canonical_hash(
        {
            "runtime": "CPYTHON_STDLIB",
            "execution_model": "COMPLETED_BAR_AVAILABILITY_CONSERVATIVE",
            "stop_trigger_model_version": SUPPORTED_TRIGGER_MODEL_VERSION,
            "base_interval_seconds": 60,
            "numeric_quantization": "6DP_ROUND_HALF_UP",
        }
    )
    return MachineOperationalization(
        operationalization_reference="src/holy_grail_machine.py",
        code_hash=MACHINE_IMPLEMENTATION_BINDING.sha256,
        environment_hash=environment_hash,
        required_feature_versions=required_feature_versions,
        parameter_identities=tuple(sorted(parameter_identity(item) for item in strategy_parameters())),
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
        ambiguity_status=AmbiguityStatus.NONE,
        ambiguity_notes=(
            "FGH-GATE-01..06 and the swing/exit machine conventions are Owner-decided "
            "(2026-08-20).  The four operationalization prerequisites - BASE-to-machine "
            "interval, ADX rising window, swing confirmation counts, and trailing-stop machine "
            "definition - are bound by the Owner approval of 2026-08-21 "
            "(HOLY_GRAIL_MACHINE_OPERATIONALIZATION_OWNER_APPROVAL_2026-08-21).  No critical "
            "ambiguity remains open."
        ),
        primary_required=True,
        source_variant_count=1,
        observation_surfaces=_observation_surfaces(),
        unavailable_inputs=(),
        instrument_scope=("ag", "al", "au", "cu", "ni", "rb"),
        timeframe_scope=(BASE_TIME_INTERVAL,),
        project_transfer_status=TransferStatus.INFERRED,
        machine=_machine_operationalization(),
        data_exposure_history_reference=DATA_EXPOSURE_HISTORY_REFERENCE,
        parent_contract_id=PARENT_CONTRACT_ID,
        created_at=CREATED_AT,
    )


def build_payload() -> dict[str, Any]:
    evidence = _load_session_evidence()
    contract = build_contract()
    validation = validate_contract(contract)
    if not validation.ready:
        raise ValueError(
            "Holy Grail V0.4 unexpectedly failed machine readiness: "
            + ",".join(validation.blockers)
        )
    machine = contract.machine
    if machine is None:
        raise ValueError("Holy Grail V0.4 must install a machine operationalization")
    return {
        "artifact": "RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_4",
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
        "primary_selection_identity": contract.primary_selection_identity,
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
        "machine_operationalization": {
            "operationalization_reference": machine.operationalization_reference,
            "code_hash": machine.code_hash,
            "environment_hash": machine.environment_hash,
            "required_feature_versions": list(machine.required_feature_versions),
            "parameter_identities": list(machine.parameter_identities),
            "machine_identity": machine.machine_identity,
        },
        "machine_readiness": validation.readiness.value,
        "machine_readiness_blockers": list(validation.blockers),
        "owner_approved_decisions": dict(OWNER_APPROVED_DECISIONS),
        "open_prerequisites": dict(OPEN_PREREQUISITES),
        "unresolved_machine_definitions": list(UNRESOLVED_MACHINE_DEFINITIONS),
        "owner_approval_evidence": OWNER_APPROVAL_EVIDENCE,
        "source_evidence_recorded_claim_count": evidence["recorded_claim_count"],
        "final_decision": {
            "MACHINE_READY": "YES",
            "PRIMARY_FREEZE_READY": "YES",
            "STRATEGY_IDENTITY_CREATED": "NO",
            "OUTCOME_TEST_REGISTERED": "NO",
            "CANDIDATE_OUTCOME_DATA_USED": "NO",
            "RESEARCH_FIREWALL_UNLOCKED": "NO",
        },
    }


def main() -> None:
    payload = build_payload()
    if payload["machine_readiness"] != "MACHINE_READY":
        raise SystemExit("Holy Grail V0.4 unexpectedly became NOT_MACHINE_READY")
    if payload["final_decision"]["MACHINE_READY"] != "YES":
        raise SystemExit("Holy Grail V0.4 final decision does not mark MACHINE_READY")
    OUTPUT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

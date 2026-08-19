"""PACKAGE_C_PREFLIGHT_PLAYBOOK_PROTOCOL_REPRODUCTION_V0_1 diagnostic tool.

This is a DIAGNOSTIC / defect-reproduction tool, NOT a repair task and NOT part
of the default unittest suite.  Its purpose is to prove, on the real
`origin/main` code, the P-01..P-05 Playbook Contract findings from the second
full-project adversarial audit:

  docs/reviews/FULL_PROJECT_SECOND_PASS_ADVERSARIAL_AUDIT_2026-08-20.md (Part B)

Rules followed (per the Package C preflight mandate):
- NO production code is modified.
- NO frozen Protocol / Holy Grail / CURRENT_STATE is modified.
- Every reproduction uses a SYNTHETIC `PlaybookContract` fixture.
- NO Raschke outcome data is used and NO market data is read.

Behavior contract (matches the Package D/E reproduction conventions):
- If current behavior matches the audit finding  -> print ``Pxx=REPRODUCED``.
- If current behavior contradicts the audit      -> print ``Pxx=AUDIT_FINDING_INACCURATE``.
- If the reproduction itself hits an unexpected
  environment error                              -> print ``Pxx=REPRO_ERROR``.
- The script ALWAYS exits 0: it is a diagnostic probe, so an unexpected error
  in one probe must not be reported as a suite failure.

Run from the repository root:

  python tools/reproduce_package_c_findings.py
"""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

# Bootstrap: allow ``import src`` when run as a plain script from anywhere
# inside the checkout (``python tools/reproduce_package_c_findings.py``).
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.playbook_contract import (  # noqa: E402
    AmbiguityStatus,
    ClaimStatus,
    InterpretationBranch,
    MachineOperationalization,
    MachineReadiness,
    ObservationSurface,
    ObservabilityStatus,
    PlaybookContract,
    SourceClaimRef,
    TransferStatus,
    bridge_to_strategy_identity,
    validate_contract,
)
from src.strategy_evidence import TypedParameter  # noqa: E402

RESULTS: dict[str, str] = {}


# ---------------------------------------------------------------------------
# Synthetic fixture helpers (generic, no candidate family, no market data)
# ---------------------------------------------------------------------------

def _source_claim(claim_id: str) -> SourceClaimRef:
    return SourceClaimRef(
        claim_id=claim_id,
        source_id=f"src-{claim_id}",
        source_anchor=f"anchor-{claim_id}",
        claim_status=ClaimStatus.EXPLICIT,
    )


def _branch(branch_id: str, claim_ids: tuple[str, ...], *, primary: bool) -> InterpretationBranch:
    return InterpretationBranch(
        branch_id=branch_id,
        source_claim_ids=claim_ids,
        source_basis=f"basis-{branch_id}",
        transfer_status=TransferStatus.EXPLICIT,
        primary_selected=primary,
    )


def _surface(surface_id: str, status: ObservabilityStatus, missing: tuple[str, ...] = ()) -> ObservationSurface:
    return ObservationSurface(
        surface_id=surface_id,
        required=True,
        observability_status=status,
        missing_inputs=missing,
    )


def _machine() -> MachineOperationalization:
    return MachineOperationalization(
        operationalization_reference="op-ref-v1",
        code_hash="code-hash-v1",
        environment_hash="env-hash-v1",
        required_feature_versions=("feature-v1",),
        parameter_identities=(),
    )


def _ready_contract(**overrides) -> PlaybookContract:
    """A synthetic contract that satisfies every current machine-ready check."""
    base = dict(
        schema_version="0.1",
        contract_version="0.1.0",
        contract_id="pb-package-c-repro-fixture",
        research_lineage_id="research-lineage-fixture",
        family_id="fixture-family",
        source_claims=(_source_claim("c1"),),
        source_bundle_identity="bundle-id-v1",
        source_bundle_hash="bundle-hash-v1",
        source_only_session_identity="session-id-v1",
        source_scope="deterministic-fixture",
        interpretations=(_branch("b1", ("c1",), primary=True),),
        ambiguity_status=AmbiguityStatus.NONE,
        ambiguity_notes=None,
        primary_required=True,
        source_variant_count=1,
        observation_surfaces=(_surface("price", ObservabilityStatus.OBSERVABLE_NOW),),
        unavailable_inputs=(),
        instrument_scope=("cu",),
        timeframe_scope=("5m",),
        project_transfer_status=TransferStatus.EXPLICIT,
        machine=_machine(),
        data_exposure_history_reference="exposure-fixture-v1",
        parent_contract_id=None,
        created_at="2026-08-20T00:00:00Z",
    )
    base.update(overrides)
    return PlaybookContract(**base)


def _finish(key: str, value: str) -> str:
    RESULTS[key] = value
    return value


# ---------------------------------------------------------------------------
# P-01: one PRIMARY per contract, not one PRIMARY per source-faithful claim
# ---------------------------------------------------------------------------

def reproduce_p01() -> str:
    contract = _ready_contract(
        source_claims=(_source_claim("c1"), _source_claim("c2")),
        interpretations=(
            _branch("b1", ("c1",), primary=True),
            _branch("b2", ("c2",), primary=False),
        ),
        ambiguity_status=AmbiguityStatus.NONE,  # non-blocking per the mandate
        project_transfer_status=TransferStatus.EXPLICIT,
    )
    result = validate_contract(contract)
    c2_primary = [
        b.branch_id
        for b in contract.interpretations
        if b.source_claim_ids == ("c2",) and b.primary_selected
    ]
    print("[P-01] source claims =", [c.claim_id for c in contract.source_claims])
    print("[P-01] primary branches =",
          [b.branch_id for b in contract.interpretations if b.primary_selected])
    print("[P-01] claim c2 has its own PRIMARY branch =", c2_primary)
    print("[P-01] validate_contract readiness =", result.readiness.value, "blockers =", result.blockers)
    # Defect reproduced iff the validator is machine-ready even though claim c2
    # has no PRIMARY interpretation of its own.
    if result.readiness is MachineReadiness.MACHINE_READY and not c2_primary:
        return _finish("P01", "REPRODUCED")
    return _finish("P01", "AUDIT_FINDING_INACCURATE")


# ---------------------------------------------------------------------------
# P-02: ambiguity_status is caller self-attestation (no field-level inventory)
# ---------------------------------------------------------------------------

def reproduce_p02() -> str:
    # Two contracts identical in every field except the caller-supplied enum.
    unresolved = _ready_contract(ambiguity_status=AmbiguityStatus.UNRESOLVED_CRITICAL)
    resolved = replace(unresolved, ambiguity_status=AmbiguityStatus.NONE)
    ru = validate_contract(unresolved)
    rr = validate_contract(resolved)
    diff_fields = [
        f.name
        for f in PlaybookContract.__dataclass_fields__.values()
        if getattr(unresolved, f.name) != getattr(resolved, f.name)
    ]
    print("[P-02] only differing contract fields =", diff_fields)
    print("[P-02] UNRESOLVED_CRITICAL readiness =", ru.readiness.value, "blockers =", ru.blockers)
    print("[P-02] NONE readiness =", rr.readiness.value, "blockers =", rr.blockers)
    # Defect reproduced iff flipping only the caller-set enum removes the
    # UNRESOLVED_CRITICAL_AMBIGUITY blocker with no field-level proof required.
    if "UNRESOLVED_CRITICAL_AMBIGUITY" in ru.blockers and rr.readiness is MachineReadiness.MACHINE_READY:
        return _finish("P02", "REPRODUCED")
    return _finish("P02", "AUDIT_FINDING_INACCURATE")


# ---------------------------------------------------------------------------
# P-03: PARTIALLY_OBSERVABLE required surface does not block MACHINE_READY
# ---------------------------------------------------------------------------

def reproduce_p03() -> str:
    contract = _ready_contract(
        observation_surfaces=(
            _surface(
                "price",
                ObservabilityStatus.PARTIALLY_OBSERVABLE,
                missing=("order-flow",),
            ),
        ),
        # The mandate forbids also stuffing the surface id into
        # contract.unavailable_inputs, which would trigger the OTHER existing
        # REQUIRED_INPUT_NOT_OBSERVABLE blocker.
        unavailable_inputs=(),
    )
    result = validate_contract(contract)
    print("[P-03] required surface observability =", contract.observation_surfaces[0].observability_status.value)
    print("[P-03] required surface missing_inputs =", contract.observation_surfaces[0].missing_inputs)
    print("[P-03] unavailable_inputs =", contract.unavailable_inputs)
    print("[P-03] validate_contract readiness =", result.readiness.value, "blockers =", result.blockers)
    if result.readiness is MachineReadiness.MACHINE_READY:
        return _finish("P03", "REPRODUCED")
    return _finish("P03", "AUDIT_FINDING_INACCURATE")


# ---------------------------------------------------------------------------
# P-04: UNKNOWN project transfer status does not block MACHINE_READY
# ---------------------------------------------------------------------------

def reproduce_p04() -> str:
    contract = _ready_contract(project_transfer_status=TransferStatus.UNKNOWN)
    result = validate_contract(contract)
    print("[P-04] project_transfer_status =", contract.project_transfer_status.value)
    print("[P-04] branch transfer statuses =",
          [b.transfer_status.value for b in contract.interpretations])
    print("[P-04] validate_contract readiness =", result.readiness.value, "blockers =", result.blockers)
    if result.readiness is MachineReadiness.MACHINE_READY:
        return _finish("P04", "REPRODUCED")
    return _finish("P04", "AUDIT_FINDING_INACCURATE")


# ---------------------------------------------------------------------------
# P-05: multiple timeframes silently collapse into one StrategyIdentity string
# ---------------------------------------------------------------------------

def reproduce_p05() -> str:
    contract = _ready_contract(timeframe_scope=("15m", "60m"))
    result = validate_contract(contract)
    print("[P-05] timeframe_scope =", contract.timeframe_scope)
    print("[P-05] validate_contract readiness =", result.readiness.value, "blockers =", result.blockers)
    if result.readiness is not MachineReadiness.MACHINE_READY:
        return _finish("P05", "AUDIT_FINDING_INACCURATE")
    identity = bridge_to_strategy_identity(
        contract,
        parameters=(),
        code_hash="code-hash-v1",
        environment_hash="env-hash-v1",
        required_feature_versions=("feature-v1",),
        data_exposure_history_reference="exposure-fixture-v1",
    )
    print("[P-05] StrategyIdentity.timeframe =", repr(identity.timeframe))
    if identity.timeframe == "15m,60m":
        return _finish("P05", "REPRODUCED")
    return _finish("P05", "AUDIT_FINDING_INACCURATE")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    probes = [
        ("P01", reproduce_p01),
        ("P02", reproduce_p02),
        ("P03", reproduce_p03),
        ("P04", reproduce_p04),
        ("P05", reproduce_p05),
    ]
    for key, fn in probes:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 - a diagnostic probe must not abort the run
            print(f"[{key}] exception during reproduction: {type(exc).__name__}: {exc}")
            RESULTS[key] = "REPRO_ERROR"

    print()
    for key, _ in probes:
        print(f"{key}={RESULTS[key]}")
    print()
    print("STATUS=PREFLIGHT_DEFECT_REPRODUCTION_COMPLETE")
    print("PRODUCTION_CODE_CHANGED=NO")
    print("NO_CANDIDATE_OUTCOME_DATA_USED=YES")

    # Diagnostic completeness is the deliverable; exit 0 regardless.
    return 0


if __name__ == "__main__":
    sys.exit(main())

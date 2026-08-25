"""Build the no-outcome three-layer pre-Shadow technical gate evidence."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from src.jianghe_source_only_verification import _repository_blob_bytes
from src.pre_shadow_gate import PreShadowGateV02Inputs, PreShadowTechnicalGateV02


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "evidence" / "PRE_SHADOW_GATE_V0_2.json"


def build_payload() -> dict[str, object]:
    decision = PreShadowTechnicalGateV02().evaluate(PreShadowGateV02Inputs(
        strategy_identity_frozen=True, machine_ready=True,
        e07_runtime_mapping_wired=True, candidate_eligibility_active=True,
        stop_oco_execution_verified=True, runtime_recovery_verified=True,
        safety_verified=True, authority_ingestion_ready=True,
        ledger_reconciliation_verified=True, statistical_profile_locked=False,
        research_wave_locked=False, shadow_authorized=False,
        fee_margin_fact_configured=False, price_limit_fact_configured=False,
        slippage_policy_configured=False, source_only_verified=True,
        outcome_exposure_clean=True,
    ))
    return {
        "artifact": "PRE_SHADOW_GATE_V0_2",
        "gate_module_sha256": sha256(
            _repository_blob_bytes(ROOT / "src" / "pre_shadow_gate.py")
        ).hexdigest(),
        "engineering_ready": decision.engineering_ready,
        "research_method_ready": decision.research_method_ready,
        "authorized_to_start": decision.authorized_to_start,
        "missing_engineering_controls": list(decision.missing_engineering_controls),
        "missing_research_controls": list(decision.missing_research_controls),
        "missing_authorization_controls": list(decision.missing_authorization_controls),
        "identity": decision.identity_id,
        "candidate_outcome_data_used": "NO",
        "prospective_shadow_forward": "NOT_AUTHORIZED",
    }


def main() -> None:
    OUT.write_text(json.dumps(build_payload(), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

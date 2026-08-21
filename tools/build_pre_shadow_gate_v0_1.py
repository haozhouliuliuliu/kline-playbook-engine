"""Build the no-outcome PreShadowGate evidence record."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from src.pre_shadow_gate import PreShadowGate, PreShadowGateInputs


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "evidence" / "PRE_SHADOW_GATE_V0_1.json"


def build_payload() -> dict[str, object]:
    gate = PreShadowGate()
    decision = gate.evaluate(PreShadowGateInputs(
        strategy_identity_frozen=True,
        machine_ready=True,
        statistical_profile_locked=False,
        research_wave_locked=False,
        e07_runtime_mapping_wired=True,
        candidate_eligibility_active=True,
        runtime_adapter_verified=True,
        fee_margin_authority_configured=False,
        price_limit_authority_configured=False,
        slippage_authority_configured=False,
        source_only_verified=True,
        outcome_exposure_clean=True,
        shadow_authorized=False,
    ))
    return {
        "artifact": "PRE_SHADOW_GATE_V0_1",
        "gate_module_sha256": sha256((ROOT / "src" / "pre_shadow_gate.py").read_bytes()).hexdigest(),
        "decision": {
            "technically_ready": decision.technically_ready,
            "authorized_to_start": decision.authorized_to_start,
            "missing_controls": list(decision.missing_controls),
            "identity": decision.identity_id,
        },
        "candidate_outcome_data_used": "NO",
        "prospective_shadow_forward": "NOT_AUTHORIZED",
    }


def main() -> None:
    OUT.write_text(json.dumps(build_payload(), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

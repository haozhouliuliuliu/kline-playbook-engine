"""Machine-readable pre-Shadow readiness gate; it never authorizes Shadow."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


def _hash(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class PreShadowGateInputs:
    strategy_identity_frozen: bool
    machine_ready: bool
    statistical_profile_locked: bool
    research_wave_locked: bool
    e07_runtime_mapping_wired: bool
    candidate_eligibility_active: bool
    runtime_adapter_verified: bool
    fee_margin_authority_configured: bool
    price_limit_authority_configured: bool
    slippage_authority_configured: bool
    source_only_verified: bool
    outcome_exposure_clean: bool
    shadow_authorized: bool


@dataclass(frozen=True)
class PreShadowGateDecision:
    technically_ready: bool
    authorized_to_start: bool
    missing_controls: tuple[str, ...]
    identity_id: str


class PreShadowGate:
    REQUIRED = ("strategy_identity_frozen", "machine_ready", "statistical_profile_locked", "research_wave_locked", "e07_runtime_mapping_wired", "candidate_eligibility_active", "runtime_adapter_verified", "fee_margin_authority_configured", "price_limit_authority_configured", "slippage_authority_configured", "source_only_verified", "outcome_exposure_clean")

    def evaluate(self, inputs: PreShadowGateInputs) -> PreShadowGateDecision:
        missing = tuple(name for name in self.REQUIRED if not getattr(inputs, name))
        technical = not missing
        identity = _hash({"inputs": inputs.__dict__, "missing": missing, "technical": technical, "authorized": technical and inputs.shadow_authorized})
        return PreShadowGateDecision(technical, technical and inputs.shadow_authorized, missing, identity)

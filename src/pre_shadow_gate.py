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


@dataclass(frozen=True)
class PreShadowGateV02Inputs:
    strategy_identity_frozen: bool
    machine_ready: bool
    e07_runtime_mapping_wired: bool
    candidate_eligibility_active: bool
    stop_oco_execution_verified: bool
    runtime_recovery_verified: bool
    safety_verified: bool
    authority_ingestion_ready: bool
    ledger_reconciliation_verified: bool
    statistical_profile_locked: bool
    research_wave_locked: bool
    shadow_authorized: bool
    fee_margin_fact_configured: bool
    price_limit_fact_configured: bool
    slippage_policy_configured: bool
    source_only_verified: bool
    outcome_exposure_clean: bool


@dataclass(frozen=True)
class PreShadowGateV02Decision:
    engineering_ready: bool
    research_method_ready: bool
    authorized_to_start: bool
    missing_engineering_controls: tuple[str, ...]
    missing_research_controls: tuple[str, ...]
    missing_authorization_controls: tuple[str, ...]
    identity_id: str


class PreShadowTechnicalGateV02:
    """Three-layer gate: engineering, research method, then authorization."""

    ENGINEERING = ("strategy_identity_frozen", "machine_ready", "e07_runtime_mapping_wired", "candidate_eligibility_active", "stop_oco_execution_verified", "runtime_recovery_verified", "safety_verified", "authority_ingestion_ready", "ledger_reconciliation_verified", "source_only_verified", "outcome_exposure_clean")
    RESEARCH = ("statistical_profile_locked", "research_wave_locked")
    AUTHORIZATION = ("shadow_authorized", "fee_margin_fact_configured", "price_limit_fact_configured", "slippage_policy_configured")

    def evaluate(self, inputs: PreShadowGateV02Inputs) -> PreShadowGateV02Decision:
        engineering_missing = tuple(name for name in self.ENGINEERING if not getattr(inputs, name))
        research_missing = tuple(name for name in self.RESEARCH if not getattr(inputs, name))
        authorization_missing = tuple(name for name in self.AUTHORIZATION if not getattr(inputs, name))
        engineering_ready = not engineering_missing
        research_ready = not research_missing
        authorized = engineering_ready and research_ready and not authorization_missing
        identity = _hash({"inputs": inputs.__dict__, "engineering_missing": engineering_missing, "research_missing": research_missing, "authorization_missing": authorization_missing, "engineering_ready": engineering_ready, "research_ready": research_ready, "authorized": authorized})
        return PreShadowGateV02Decision(engineering_ready, research_ready, authorized, engineering_missing, research_missing, authorization_missing, identity)

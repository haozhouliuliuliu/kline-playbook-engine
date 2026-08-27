"""Result-independent activation bindings for future real-time PAPER execution."""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json

PAPER_ACTIVATION_PROFILE_SCHEMA_VERSION = "KPE_PAPER_ACTIVATION_PROFILE_V0_1"

class PaperActivationStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"

@dataclass(frozen=True)
class PaperActivationProfile:
    profile_id: str
    status: PaperActivationStatus
    execution_mode: str
    tqsdk_runtime_version: str
    live_data_policy_identity: str | None
    sizing_policy_identity: str | None
    execution_price_policy_identity: str | None
    close_offset_policy_identity: str | None
    risk_policy_identity: str | None
    broker_adapter_identity: str | None
    allowed_contracts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.status, PaperActivationStatus):
            raise ValueError("paper activation status must be explicit")
        if not isinstance(self.profile_id, str) or not self.profile_id.strip():
            raise ValueError("paper activation profile requires an id")
        if self.execution_mode != "PAPER":
            raise ValueError("paper activation profile execution_mode must be PAPER")
        if not isinstance(self.tqsdk_runtime_version, str) or not self.tqsdk_runtime_version.strip():
            raise ValueError("paper activation profile requires an explicit TqSdk runtime version")
        if any(not isinstance(c, str) or not c.strip() or c != c.strip() for c in self.allowed_contracts):
            raise ValueError("paper activation contracts must be canonical non-empty strings")
        if len(self.allowed_contracts) != len(set(self.allowed_contracts)):
            raise ValueError("paper activation contracts must be unique")
        bindings = (
            self.live_data_policy_identity,
            self.sizing_policy_identity,
            self.execution_price_policy_identity,
            self.close_offset_policy_identity,
            self.risk_policy_identity,
            self.broker_adapter_identity,
        )
        for value in bindings:
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError("paper activation policy identities must be non-empty when supplied")
        if self.status is PaperActivationStatus.ACTIVE:
            if not self.allowed_contracts:
                raise ValueError("ACTIVE paper activation requires at least one contract")
            if any(value is None for value in bindings):
                raise ValueError("ACTIVE paper activation requires every execution policy binding")

    @property
    def identity_id(self) -> str:
        payload = {
            "schema_version": PAPER_ACTIVATION_PROFILE_SCHEMA_VERSION,
            "profile_id": self.profile_id,
            "status": self.status.value,
            "execution_mode": self.execution_mode,
            "tqsdk_runtime_version": self.tqsdk_runtime_version,
            "live_data_policy_identity": self.live_data_policy_identity,
            "sizing_policy_identity": self.sizing_policy_identity,
            "execution_price_policy_identity": self.execution_price_policy_identity,
            "close_offset_policy_identity": self.close_offset_policy_identity,
            "risk_policy_identity": self.risk_policy_identity,
            "broker_adapter_identity": self.broker_adapter_identity,
            "allowed_contracts": sorted(self.allowed_contracts),
        }
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        return sha256(encoded.encode("utf-8")).hexdigest()

    def require_active_for(self, concrete_contract_id: str) -> None:
        if self.status is not PaperActivationStatus.ACTIVE:
            raise PermissionError("PAPER_ACTIVATION_PROFILE_NOT_ACTIVE")
        if concrete_contract_id not in self.allowed_contracts:
            raise PermissionError("PAPER_ACTIVATION_CONTRACT_NOT_ALLOWED")

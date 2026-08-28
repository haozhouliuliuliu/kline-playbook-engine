"""Executable PAPER binding identities and external-tool role verification.

The activation profile contains approved identity strings.  This module proves
that those strings name the exact injected implementations instead of trusting
caller-declared labels.  It performs no network, credential, provider, account
or order action.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json

from src.paper_activation_profile import PaperActivationProfile

PAPER_RUNTIME_BINDINGS_VERSION = "KPE_PAPER_RUNTIME_BINDINGS_V0_1"


def _hash(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )
    return sha256(encoded.encode("utf-8")).hexdigest()


def executable_identity(value: object, name: str) -> str:
    """Read a mechanically exposed implementation identity.

    Identity strings supplied separately from the implementation are rejected;
    the injected adapter/policy itself must expose ``identity_id``.
    """
    identity = getattr(value, "identity_id", None)
    if callable(identity):
        identity = identity()
    if not isinstance(identity, str) or not identity.strip():
        raise ValueError(f"{name} must expose a non-empty identity_id")
    return identity.strip()


class PaperToolRoleStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    VERIFIED = "VERIFIED"
    ADOPTED = "ADOPTED"


@dataclass(frozen=True)
class PaperToolRoleBinding:
    tool_name: str
    role: str
    status: PaperToolRoleStatus
    runtime_version: str
    evidence_identity: str | None = None

    def __post_init__(self) -> None:
        for value, name in (
            (self.tool_name, "paper tool name"),
            (self.role, "paper tool role"),
            (self.runtime_version, "paper tool runtime version"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if not isinstance(self.status, PaperToolRoleStatus):
            raise ValueError("paper tool role status must be explicit")
        if self.evidence_identity is not None and (
            not isinstance(self.evidence_identity, str) or not self.evidence_identity.strip()
        ):
            raise ValueError("paper tool evidence identity must be non-empty when supplied")
        if self.status in {PaperToolRoleStatus.VERIFIED, PaperToolRoleStatus.ADOPTED} and not self.evidence_identity:
            raise ValueError("verified/adopted PAPER tool role requires evidence identity")

    @property
    def identity_id(self) -> str:
        return _hash({
            "schema_version": PAPER_RUNTIME_BINDINGS_VERSION,
            "tool_name": self.tool_name,
            "role": self.role,
            "status": self.status.value,
            "runtime_version": self.runtime_version,
            "evidence_identity": self.evidence_identity,
        })


@dataclass(frozen=True)
class PaperExecutableBindings:
    """The exact implementations named by one activation profile."""

    live_data_policy: object
    sizing_policy: object
    execution_price_policy: object
    close_offset_policy: object
    risk_policy: object
    broker_adapter: object

    @property
    def identities(self) -> dict[str, str]:
        return {
            "live_data_policy_identity": executable_identity(
                self.live_data_policy, "live-data policy"
            ),
            "sizing_policy_identity": executable_identity(
                self.sizing_policy, "sizing policy"
            ),
            "execution_price_policy_identity": executable_identity(
                self.execution_price_policy, "execution-price policy"
            ),
            "close_offset_policy_identity": executable_identity(
                self.close_offset_policy, "close-offset policy"
            ),
            "risk_policy_identity": executable_identity(self.risk_policy, "risk policy"),
            "broker_adapter_identity": executable_identity(
                self.broker_adapter, "broker adapter"
            ),
        }

    @property
    def identity_id(self) -> str:
        return _hash({
            "schema_version": PAPER_RUNTIME_BINDINGS_VERSION,
            "bindings": self.identities,
        })

    def require_matches(self, profile: PaperActivationProfile) -> None:
        if not isinstance(profile, PaperActivationProfile):
            raise TypeError("executable binding check requires PaperActivationProfile")
        mismatches = [
            name
            for name, actual in self.identities.items()
            if getattr(profile, name) != actual
        ]
        if mismatches:
            raise ValueError(
                "PAPER_EXECUTABLE_BINDING_MISMATCH:" + ",".join(sorted(mismatches))
            )


__all__ = [
    "PAPER_RUNTIME_BINDINGS_VERSION",
    "PaperExecutableBindings",
    "PaperToolRoleBinding",
    "PaperToolRoleStatus",
    "executable_identity",
]

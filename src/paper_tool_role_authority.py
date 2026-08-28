"""Canonical TOOL_REGISTRY-backed authority for the TqSdk PAPER role.

This module only reads the repository's canonical tool registry.  It performs
no package import, credential lookup, login, network, provider or broker action.
Caller-created runtime bindings are claims checked against this authority; they
never become the authority themselves.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re

from src.paper_runtime_bindings import PaperToolRoleBinding, PaperToolRoleStatus

TQSDK_EXTERNAL_PAPER_ROLE = "EXTERNAL_PAPER"
_REGISTRY_PATH = Path(__file__).resolve().parents[1] / "TOOL_REGISTRY.md"


@dataclass(frozen=True)
class PaperToolRoleVerification:
    adopted: bool
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class CanonicalPaperToolRoleAuthority:
    tool_name: str
    role: str
    status: PaperToolRoleStatus
    runtime_version: str
    evidence_identity: str

    def verify(
        self,
        binding: PaperToolRoleBinding | None,
        *,
        executable_runtime_version: str,
    ) -> PaperToolRoleVerification:
        blockers: list[str] = []
        if self.status is not PaperToolRoleStatus.ADOPTED:
            blockers.append("CANONICAL_PAPER_ROLE_NOT_ADOPTED")
        if binding is None:
            blockers.append("PAPER_ROLE_BINDING_MISSING")
        else:
            if binding.tool_name != self.tool_name or binding.role != self.role:
                blockers.append("PAPER_ROLE_SCOPE_MISMATCH")
            if binding.status is not self.status:
                blockers.append("PAPER_ROLE_STATUS_MISMATCH")
            if binding.evidence_identity != self.evidence_identity:
                blockers.append("PAPER_ROLE_EVIDENCE_MISMATCH")
            if binding.runtime_version != self.runtime_version:
                blockers.append("PAPER_ROLE_RUNTIME_VERSION_MISMATCH")
        if (
            not isinstance(executable_runtime_version, str)
            or not executable_runtime_version.strip()
            or executable_runtime_version.strip() != self.runtime_version
        ):
            blockers.append("PAPER_EXECUTABLE_RUNTIME_VERSION_MISMATCH")
        unique = tuple(sorted(set(blockers)))
        return PaperToolRoleVerification(adopted=not unique, blockers=unique)


def current_tqsdk_paper_role_authority() -> CanonicalPaperToolRoleAuthority:
    """Load the one project-owned registry path; callers cannot redirect it."""
    try:
        text = _REGISTRY_PATH.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise RuntimeError("CANONICAL_TOOL_REGISTRY_UNREADABLE") from error
    section_match = re.search(
        r"(?ms)^## 3\. TqSdk\s*$\n(?P<section>.*?)(?=^## \d+\.|\Z)", text
    )
    if section_match is None:
        raise RuntimeError("CANONICAL_TQSDK_REGISTRY_ENTRY_MISSING")
    section = section_match.group("section")
    status_match = re.search(r"(?m)^`STATUS = (CANDIDATE|VERIFIED|ADOPTED)`\s*$", section)
    version_match = re.search(r"(?m)^`tqsdk = ([^`]+)`\s*$", section)
    role_match = re.search(
        r"(?ms)^Roles?:\s*$\n(?P<roles>.*?)(?=^Verified runtime:|^Authority/evidence:|\Z)",
        section,
    )
    if status_match is None or version_match is None or role_match is None:
        raise RuntimeError("CANONICAL_TQSDK_REGISTRY_ENTRY_MALFORMED")
    governed_roles = set(re.findall(r"`([^`]+)`", role_match.group("roles")))
    status = (
        PaperToolRoleStatus(status_match.group(1))
        if TQSDK_EXTERNAL_PAPER_ROLE in governed_roles
        else PaperToolRoleStatus.CANDIDATE
    )
    evidence_identity = sha256(section.encode("utf-8")).hexdigest()
    return CanonicalPaperToolRoleAuthority(
        tool_name="TqSdk",
        role=TQSDK_EXTERNAL_PAPER_ROLE,
        status=status,
        runtime_version=version_match.group(1).strip(),
        evidence_identity=evidence_identity,
    )


__all__ = [
    "CanonicalPaperToolRoleAuthority",
    "PaperToolRoleVerification",
    "TQSDK_EXTERNAL_PAPER_ROLE",
    "current_tqsdk_paper_role_authority",
]

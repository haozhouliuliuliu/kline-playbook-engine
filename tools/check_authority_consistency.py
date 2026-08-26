#!/usr/bin/env python3
"""Fail-closed structural checks for active project authority ownership.

This checker does not decide research/trading semantics. It protects the repository
memory topology: one concern has one canonical owner, volatile current state stays
in CURRENT_STATE.md, takeover owners exist, and the current provider-smoke machine
authority cannot contradict an Owner hold.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_OWNER_FILES = (
    "00_READ_FIRST.md",
    "PROJECT_GOVERNANCE.md",
    "AGENTS.md",
    "ARCHITECTURE_BASELINE.md",
    "TOOL_REGISTRY.md",
    "PROJECT_DIRECTION.md",
    "PROJECT_BRAIN_RUNTIME_BRIEF.md",
    "CURRENT_STATE.md",
    "README.md",
    "KNOWN_LIMITATIONS_AND_TECH_DEBT.md",
)

STABLE_OWNER_FILES = (
    "00_READ_FIRST.md",
    "PROJECT_GOVERNANCE.md",
    "AGENTS.md",
    "ARCHITECTURE_BASELINE.md",
    "TOOL_REGISTRY.md",
    "PROJECT_DIRECTION.md",
    "PROJECT_BRAIN_RUNTIME_BRIEF.md",
    "README.md",
    "KNOWN_LIMITATIONS_AND_TECH_DEBT.md",
)

VOLATILE_ASSIGNMENT_KEYS = (
    "CURRENT_ACTIVITY",
    "CURRENT_WORK_PACKAGE",
    "WORK_PACKAGE_PHASE",
    "NEXT_TASK",
    "PROVIDER_SMOKE_EXECUTION",
    "NEXT_EXPLICIT_PAID_SLOT",
    "REAL_DEEPSEEK_PROVIDER_CALLS",
    "THREE_CALL_SMOKE_MACHINE_AUTHORITY_STATUS",
    "THREE_CALL_SMOKE_SLOT",
    "FULL_V0_1_1998_CALL_REPLAY",
)

REQUIRED_CURRENT_STATE_KEYS = (
    "CURRENT_ACTIVITY",
    "CURRENT_WORK_PACKAGE",
    "WORK_PACKAGE_PHASE",
    "NEXT_TASK",
)

TAKEOVER_OWNER_ORDER = (
    "PROJECT_GOVERNANCE.md",
    "AGENTS.md",
    "ARCHITECTURE_BASELINE.md",
    "TOOL_REGISTRY.md",
    "PROJECT_DIRECTION.md",
    "PROJECT_BRAIN_RUNTIME_BRIEF.md",
    "CURRENT_STATE.md",
)

SMOKE_AUTHORITY_PATH = Path("docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT.json")

_BACKTICK_PATH = re.compile(
    r"`((?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.(?:md|json|py|yml|yaml))`"
)


def _read(root: Path, relative: str | Path) -> str:
    return (root / relative).read_text(encoding="utf-8")


def _assignment_values(text: str, key: str) -> list[str]:
    values: list[str] = []
    prefix = f"{key} ="
    for raw_line in text.splitlines():
        line = raw_line.strip().strip("`").strip()
        if line.startswith(prefix):
            values.append(line[len(prefix):].strip())
    return values


def _canonical_identity(payload: dict[str, object]) -> str:
    without_identity = dict(payload)
    without_identity.pop("authority_identity", None)
    encoded = json.dumps(
        without_identity,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )
    return sha256(encoded.encode("utf-8")).hexdigest()


def _check_required_files(root: Path) -> Iterable[str]:
    for relative in REQUIRED_OWNER_FILES:
        if not (root / relative).is_file():
            yield f"required canonical owner is missing: {relative}"


def _check_takeover_navigation(root: Path) -> Iterable[str]:
    read_first = _read(root, "00_READ_FIRST.md")
    positions: list[int] = []
    for relative in TAKEOVER_OWNER_ORDER:
        token = f"`{relative}`"
        position = read_first.find(token)
        if position < 0:
            yield f"00_READ_FIRST.md does not name canonical takeover owner: {relative}"
        positions.append(position)
    present = [value for value in positions if value >= 0]
    if len(present) == len(positions) and present != sorted(present):
        yield "00_READ_FIRST.md canonical owner order is not stable/expected"


def _check_volatile_ownership(root: Path) -> Iterable[str]:
    for relative in STABLE_OWNER_FILES:
        text = _read(root, relative)
        for key in VOLATILE_ASSIGNMENT_KEYS:
            values = _assignment_values(text, key)
            if values:
                yield (
                    f"volatile assignment {key} leaked into stable owner {relative}: "
                    + ", ".join(values)
                )

    state = _read(root, "CURRENT_STATE.md")
    for key in REQUIRED_CURRENT_STATE_KEYS:
        values = _assignment_values(state, key)
        if len(values) != 1:
            yield f"CURRENT_STATE.md must assign {key} exactly once; found {len(values)}"


def _check_current_state_references(root: Path) -> Iterable[str]:
    state = _read(root, "CURRENT_STATE.md")
    for match in sorted(set(_BACKTICK_PATH.findall(state))):
        if not (root / match).is_file():
            yield f"CURRENT_STATE.md references missing repository path: {match}"


def _check_tool_registry(root: Path) -> Iterable[str]:
    registry = _read(root, "TOOL_REGISTRY.md")
    required_tokens = (
        "LOCAL_PROVIDER_SECRET_STORE = WINDOWS_CURRENT_USER_ENVIRONMENT_VARIABLES",
        "CREDENTIAL_ENV = DEEPSEEK_API_KEY",
        "CREDENTIAL_LOCATION = WINDOWS_CURRENT_USER_ENVIRONMENT_VARIABLES",
    )
    for token in required_tokens:
        if token not in registry:
            yield f"TOOL_REGISTRY.md is missing credential continuity contract: {token}"

    forbidden_dynamic_tokens = (
        "REAL_DEEPSEEK_PROVIDER_CALLS =",
        "NEXT_EXPLICIT_PAID_SLOT =",
    )
    for token in forbidden_dynamic_tokens:
        if token in registry:
            yield f"TOOL_REGISTRY.md improperly owns volatile paid state: {token}"


def _check_governance_identity(root: Path) -> Iterable[str]:
    governance = _read(root, "PROJECT_GOVERNANCE.md")
    required = (
        "ADOPTED_CONTRACT_VERSION = 3.1",
        "ADOPTED_CONTRACT_SHA256 = 3b5ceaaa3696375b941fd2aaba95615cf9352dcada3696b60137650bf690101e",
        "one concern, one canonical owner",
        "CURRENT_STATE.md",
    )
    for token in required:
        if token not in governance:
            yield f"PROJECT_GOVERNANCE.md missing binding governance token: {token}"


def _check_smoke_machine_authority(root: Path) -> Iterable[str]:
    path = root / SMOKE_AUTHORITY_PATH
    if not path.is_file():
        return

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        yield f"{SMOKE_AUTHORITY_PATH} must be a JSON object"
        return

    stored_identity = payload.get("authority_identity")
    computed_identity = _canonical_identity(payload)
    if stored_identity != computed_identity:
        yield (
            f"{SMOKE_AUTHORITY_PATH} authority_identity mismatch: "
            f"stored={stored_identity!r} computed={computed_identity}"
        )

    if payload.get("api_key_env") != "DEEPSEEK_API_KEY":
        yield f"{SMOKE_AUTHORITY_PATH} must bind api_key_env=DEEPSEEK_API_KEY"

    state = _read(root, "CURRENT_STATE.md")
    hold_values = _assignment_values(state, "PROVIDER_SMOKE_EXECUTION")
    if hold_values == ["OWNER_HOLD_BEFORE_FIRST_CALL"] and payload.get("status") != "REVOKED":
        yield (
            "CURRENT_STATE.md says provider smoke is on Owner hold, but machine "
            f"authority status is {payload.get('status')!r} instead of 'REVOKED'"
        )

    machine_status_values = _assignment_values(
        state, "THREE_CALL_SMOKE_MACHINE_AUTHORITY_STATUS"
    )
    if machine_status_values:
        if len(machine_status_values) != 1:
            yield "CURRENT_STATE.md must assign THREE_CALL_SMOKE_MACHINE_AUTHORITY_STATUS at most once"
        elif machine_status_values[0] != str(payload.get("status")):
            yield (
                "CURRENT_STATE.md smoke machine status does not match machine authority: "
                f"state={machine_status_values[0]!r} json={payload.get('status')!r}"
            )


def check_repository(root: Path = REPO_ROOT) -> list[str]:
    checks = (
        _check_required_files,
        _check_takeover_navigation,
        _check_volatile_ownership,
        _check_current_state_references,
        _check_tool_registry,
        _check_governance_identity,
        _check_smoke_machine_authority,
    )
    errors: list[str] = []
    for check in checks:
        errors.extend(check(root))
    return errors


def main() -> int:
    errors = check_repository(REPO_ROOT)
    if errors:
        print("AUTHORITY_CONSISTENCY = FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("AUTHORITY_CONSISTENCY = PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Pre-network fail-closed guards for the V0.1 provider-smoke runner.

These checks run BEFORE any network/provider capability exists:

- ``verify_execution_code_bound`` proves the execution-critical paths currently
  in the working tree still match the pinned ``execution_code_commit`` (blob
  comparison with CRLF normalization — not HEAD equality, because the following
  authority-only commit is expected to change the authority file only).
- ``bind_runtime_identities_to_authority`` mechanically binds the live prompt
  contract, context policy, renderer and API-key environment to the authority.
- ``validate_test_base_url`` keeps provider-endpoint overrides loopback-only and
  gated by an explicit test-only flag.
- ``positive_finite_decimal`` parses a strictly positive finite Decimal.

None of these guards read provider credentials or construct network capability.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from pathlib import Path
import subprocess
from typing import Sequence
from urllib.parse import urlparse

from src.jianghe_trading_only_prompt import TradingOnlyPromptContract
from src.replay_v0_1_smoke_authority import ProviderSmokeAuthority

EXECUTION_CRITICAL_PATHS: tuple[str, ...] = (
    "src/fixed_5m_wake_ledger.py",
    "src/replay_v0_1_orchestrator.py",
    "src/replay_v0_1_smoke_authority.py",
    "src/replay_v0_1_smoke_bridge.py",
    "src/replay_v0_1_smoke_guard.py",
    "src/replay_v0_1_smoke_visual.py",
    "tools/preflight_replay_v0_1_provider_smoke.py",
    "tools/run_replay_v0_1_provider_smoke.py",
    "integrations/deepseek-harness/replay_v0_1_smoke_bridge.ts",
    "integrations/deepseek-harness/apply_deepseek_harness_project_patch.py",
)

DEEPSEEK_API_KEY_ENV = "DEEPSEEK_API_KEY"
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


def _normalize_bytes(data: bytes) -> bytes:
    """Normalize CRLF/CR line endings to LF for deterministic source comparison."""
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _git_show(repo_root: str | Path, commit: str, relative_path: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{commit}:{relative_path}"],
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", "replace").strip()
        raise ValueError(
            f"cannot read execution-critical path {relative_path!r} at execution "
            f"commit {commit}: {detail}"
        )
    return completed.stdout


def verify_execution_code_bound(
    *,
    repo_root: str | Path,
    execution_code_commit: str,
    critical_paths: Sequence[str] = EXECUTION_CRITICAL_PATHS,
) -> None:
    """Fail closed unless execution-critical working tree matches the pinned commit.

    Compares normalized (CRLF-insensitive) blob bytes of each critical path in
    the working tree against the same path at ``execution_code_commit``.  Raises
    on any drift before any provider capability is constructed.
    """
    if not isinstance(execution_code_commit, str) or len(execution_code_commit) != 40:
        raise ValueError("execution_code_commit must be a full 40-hex git commit SHA")
    repo = Path(repo_root)
    for relative in critical_paths:
        path = repo / relative
        if not path.is_file():
            raise ValueError(f"execution-critical path is missing in the working tree: {relative}")
        current = _normalize_bytes(path.read_bytes())
        pinned = _normalize_bytes(_git_show(repo, execution_code_commit, relative))
        if current != pinned:
            raise ValueError(
                f"execution-critical path {relative!r} drifted from execution commit "
                f"{execution_code_commit}; refusing to build any provider capability"
            )


def bind_runtime_identities_to_authority(
    *,
    authority: ProviderSmokeAuthority,
    prompt_contract: TradingOnlyPromptContract,
    context_policy_identity: str,
    renderer_identity: str,
    api_key_env: str,
) -> None:
    """Mechanically bind live prompt/context/renderer/api-key identities to the authority."""
    expected_prompt = authority.prompt_identities
    actual = (
        prompt_contract.version,
        prompt_contract.identity,
        prompt_contract.system_prompt_sha256,
        prompt_contract.decision_prompt_sha256,
    )
    expected = (
        expected_prompt.prompt_contract_version,
        expected_prompt.prompt_contract_identity,
        expected_prompt.system_prompt_sha256,
        expected_prompt.decision_prompt_sha256,
    )
    if actual != expected:
        raise ValueError("live prompt identities do not match the provider-smoke authority")
    if context_policy_identity != authority.context_policy_identity:
        raise ValueError("live context_policy_identity does not match the provider-smoke authority")
    if renderer_identity != authority.renderer_identity:
        raise ValueError("live renderer_identity does not match the provider-smoke authority")
    if api_key_env != DEEPSEEK_API_KEY_ENV:
        raise ValueError("provider-smoke api_key_env must be DEEPSEEK_API_KEY")


def positive_finite_decimal(value: str, field_name: str) -> Decimal:
    """Parse a strictly positive finite Decimal; fail closed on anything else."""
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a positive finite Decimal")
    try:
        parsed = Decimal(value)
    except InvalidOperation as error:
        raise ValueError(f"{field_name} must be a positive finite Decimal") from error
    if not parsed.is_finite() or parsed <= 0:
        raise ValueError(f"{field_name} must be a positive finite Decimal")
    return parsed


def validate_test_base_url(base_url: str | None, *, allow_test: bool) -> str | None:
    """Provider-endpoint override is loopback-only and gated by an explicit test flag."""
    if base_url is None:
        return None
    if not allow_test:
        raise ValueError(
            "--base-url is test-only; production paid smoke must use the pinned endpoint"
        )
    parsed = urlparse(base_url)
    host = (parsed.hostname or "").lower()
    if host not in LOOPBACK_HOSTS:
        raise ValueError("--base-url override is only permitted for loopback test servers")
    return base_url


__all__ = [
    "DEEPSEEK_API_KEY_ENV",
    "EXECUTION_CRITICAL_PATHS",
    "bind_runtime_identities_to_authority",
    "positive_finite_decimal",
    "validate_test_base_url",
    "verify_execution_code_bound",
]

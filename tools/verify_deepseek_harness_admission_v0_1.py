#!/usr/bin/env python3
"""Offline verifier for the pinned DeepSeek Harness admission candidate.

This tool performs no provider call and requires no credential. It verifies the
exact upstream commit and source-level capabilities required before project-
specific dynamic admission work may begin.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

PINNED_SHA = "b150a551b8d465e31e418e1b2eaf5e79bbb7d28e"
PINNED_VERSION = "0.1.1-rc.2"
PINNED_MODEL = "deepseek-v4-flash-vision-exp"


class AdmissionError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AdmissionError(message)


def read(root: Path, relative: str) -> str:
    path = root / relative
    require(path.is_file(), f"missing pinned Harness file: {relative}")
    return path.read_text(encoding="utf-8")


def git_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    require(result.returncode == 0, f"cannot resolve Harness HEAD: {result.stderr.strip()}")
    return result.stdout.strip()


def verify(root: Path) -> dict[str, object]:
    require(root.is_dir(), f"Harness root does not exist: {root}")
    head = git_head(root)
    require(head == PINNED_SHA, f"Harness HEAD drift: expected {PINNED_SHA}, got {head}")

    package = json.loads(read(root, "package.json"))
    require(package.get("version") == PINNED_VERSION, "root Harness version drift")
    require(package.get("packageManager") == "pnpm@11.7.0", "pnpm pin drift")
    require(package.get("engines", {}).get("node") == "^22.19.0 || >=24.0.0", "Node engine drift")

    adapter_package = json.loads(read(root, "packages/llm/llm-deepseek/package.json"))
    require(adapter_package.get("version") == PINNED_VERSION, "DeepSeek adapter version drift")

    adapter_readme = read(root, "packages/llm/llm-deepseek/README.md")
    adapter_source = read(root, "packages/llm/llm-deepseek/src/adapter.ts")
    adapter_index = read(root, "packages/llm/llm-deepseek/src/index.ts")
    retry_source = read(root, "packages/llm/llm/src/retry-policy.ts")
    session_readme = read(root, "packages/core/session/README.md")
    architecture = read(root, "docs/architecture.md")
    sqlite_session_readme = read(root, "packages/session/session-persistence-sqlite/README.md")
    sqlite_storage_readme = read(root, "packages/storage/storage-sqlite/README.md")

    require(PINNED_MODEL in adapter_readme, "exact selected model is absent from adapter documentation")
    require("deepseek-official" in adapter_readme, "DeepSeek official provider route is absent")
    require("inputModalities" in adapter_readme and "image" in adapter_readme, "vision modality evidence is absent")
    require(PINNED_MODEL in adapter_source or PINNED_MODEL in adapter_index,
            "exact selected model is absent from adapter source")

    require("const DEFAULT_MAX_RETRIES = 5" in retry_source, "retry default source changed")
    require("maxRetries" in retry_source, "retry maxRetries configuration disappeared")
    require(".min(0)" in retry_source, "zero-retry configuration is no longer schema-valid")

    require("append-only source of truth" in session_readme, "append-only session authority evidence is absent")
    require("Persistence is intentionally not implemented here" in session_readme,
            "session persistence seam statement changed")
    require("Model-visible means logged." in architecture, "model-visible audit invariant disappeared")
    require("ctx.tools" in architecture, "project-owned tool registration seam disappeared")
    require("agent.inject()" in architecture, "bounded context injection seam disappeared")
    require("SessionEventMap" in architecture, "durable custom session event seam disappeared")

    require("SQLite `SessionPersistence` provider" in sqlite_session_readme,
            "SQLite session persistence provider evidence is absent")
    require("exact logical `SessionEvent[]`" in sqlite_session_readme,
            "exact logical session replay evidence is absent")
    require("synchronous=FULL" in sqlite_session_readme,
            "SQLite committed-append durability evidence changed")
    require("serving the `kv` facet" in sqlite_storage_readme,
            "project-owned domain KV storage seam evidence is absent")

    stale_file_risk = (
        "class FileResolutionFailure" in adapter_source
        and "providerRejectedFileId" in adapter_source
        and "staleMappings" in adapter_source
    )
    require(stale_file_risk, "expected image stale-file recovery surface changed; re-review required")

    gates = {
        "PINNED_COMMIT": "PASS",
        "PINNED_VERSION": "PASS",
        "EXACT_MODEL_ROUTE": "PASS_STATIC",
        "VISION_INPUT": "PASS_STATIC",
        "ZERO_GENERAL_RETRY_CONFIG_AVAILABLE": "PASS_STATIC",
        "APPEND_ONLY_AUDIT_SPINE": "PASS_STATIC",
        "SQLITE_SESSION_PERSISTENCE": "PASS_STATIC",
        "PROJECT_TOOL_AND_CONTEXT_SEAMS": "PASS_STATIC",
        "PROJECT_DOMAIN_STORAGE_SEAM": "PASS_STATIC",
        "IMAGE_STALE_FILE_INTERNAL_RESEND_RISK": "DETECTED__PROJECT_DYNAMIC_GATE_REQUIRED",
        "PROJECT_BOUNDED_MEMORY_RESTART_PROOF": "PENDING",
        "PROJECT_KLINE_TOOL_AUDIT_PROOF": "PENDING",
    }
    return {
        "schema_version": "deepseek-harness-admission-verifier-v0.1",
        "status": "CANDIDATE_STATIC_QUALIFIED__PROJECT_DYNAMIC_GATES_PENDING",
        "upstream_repository": "deepseek-ai/deepseek-harness",
        "pinned_commit": head,
        "pinned_version": package["version"],
        "selected_model": PINNED_MODEL,
        "provider_calls": 0,
        "credentials_required": False,
        "gates": gates,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--harness-root", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.harness_root.resolve())
    except AdmissionError as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

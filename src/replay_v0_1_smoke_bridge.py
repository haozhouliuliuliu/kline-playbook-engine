"""Provider-smoke Harness bridge and zero-cost mock transport for replay V0.1.

``HarnessOneShotBridge`` is the project-side adapter that materializes the pinned
Harness one-shot bridge script (``integrations/deepseek-harness/replay_v0_1_smoke_bridge.ts``)
into the pinned Harness checkout and runs it with ``tsx``.  One governed wake maps
to exactly one ``adapter.stream()`` model request; the bridge never retries and
never issues a hidden second request.

Safety: neither the Python bridge nor the runner may read ``DEEPSEEK_API_KEY`` or
construct any network capability before an ACTIVE provider-smoke authority is
verified.  ``HarnessOneShotBridge`` enforces that again at construction time
(defense in depth).

``SmokeDeterministicTransport`` is the zero-cost mock used by the runner tests and
the synthetic-ACTIVE mock flow.  It never touches the network.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Mapping

from src.persistent_deepseek_runtime import CURRENT_MODEL
from src.replay_v0_1_smoke_authority import ProviderSmokeAuthority, assert_smoke_authority_active

PROVIDER_SMOKE_MOCK_IDENTITY = "NO_PROVIDER_PROVIDER_SMOKE_MOCK_V0_1"
SMOKE_BRIDGE_SCRIPT_REPO = "integrations/deepseek-harness/replay_v0_1_smoke_bridge.ts"
SMOKE_BRIDGE_HARNESS_REL = "tests-kpe-replay-v0-1/replay_v0_1_smoke_bridge.ts"
SMOKE_BRIDGE_VERSION = "KPE_REPLAY_V0_1_PROVIDER_SMOKE_BRIDGE_V0_1"


def _valid_mock_response() -> str:
    return json.dumps(
        {
            "schema_version": "JIANGHE_RUNTIME_RESPONSE_V0_2",
            "family": "NONE",
            "action": "WAIT",
            "direction": "NONE",
            "attention_mode": "SCAN",
            "decision_state": "provider_smoke_mock_wait",
            "rationale": "Deterministic zero-cost provider-smoke rehearsal; no provider call occurred.",
            "declared_unknown": [],
            "principle_references": [],
            "source_references": [],
            "numeric_claims": [],
            "current_market_hypothesis": None,
            "timeframe_trend_view": [],
            "key_location_hypotheses": [],
            "expected_trigger": None,
            "invalidation_hypothesis": None,
            "open_questions": [],
        },
        ensure_ascii=False,
        sort_keys=True,
    )


@dataclass(frozen=True)
class SmokeBridgeResult:
    status: str
    provider: str
    model: str
    raw_response_text: str
    finish_reason: str
    token_usage: Mapping[str, int]
    provider_request_id: str | None
    image_count: int
    request_count: int
    error: str | None = None


class HarnessOneShotBridge:
    """One-shot bridge to the pinned Harness (one model request per wake)."""

    def __init__(
        self,
        *,
        authority: ProviderSmokeAuthority,
        harness_root: str | Path,
        repo_root: str | Path,
        api_key_env: str = "DEEPSEEK_API_KEY",
        base_url: str | None = None,
    ) -> None:
        # Fail-closed: no network capability and no credential read before ACTIVE.
        assert_smoke_authority_active(authority)
        if api_key_env != authority.api_key_env:
            raise ValueError("provider-smoke bridge API key env does not match the authority")
        self._authority = authority
        self._harness_root = Path(harness_root).resolve()
        self._repo_root = Path(repo_root).resolve()
        self._api_key_env = api_key_env
        self._base_url = base_url
        if not (self._harness_root / "node_modules" / ".bin" / "tsx.cmd").is_file():
            raise RuntimeError("pinned Harness checkout has no tsx launcher")
        self._bridge_script = self._harness_root / SMOKE_BRIDGE_HARNESS_REL

    @property
    def provider_identity(self) -> str:
        return "DEEPSEEK_HARNESS_ONE_SHOT_V0_1"

    @property
    def mock(self) -> bool:
        return False

    @property
    def provider_admitted(self) -> bool:
        return True

    def _materialize_bridge(self) -> None:
        source = self._repo_root / SMOKE_BRIDGE_SCRIPT_REPO
        if not source.is_file():
            raise RuntimeError(f"missing bridge source in repo: {source}")
        self._bridge_script.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, self._bridge_script)

    def _cleanup_bridge(self) -> None:
        try:
            if self._bridge_script.exists():
                self._bridge_script.unlink()
        except OSError:
            pass

    def execute(
        self,
        *,
        system_prompt: str,
        decision_prompt: str,
        context: Mapping[str, Any],
        png_images: tuple[bytes, ...],
    ) -> SmokeBridgeResult:
        if len(png_images) != 4:
            raise ValueError("provider smoke request must attach exactly four PNG images")
        self._materialize_bridge()
        try:
            with tempfile.TemporaryDirectory(prefix="kpe-smoke-bridge-") as tmp:
                work = Path(tmp)
                bundle_path = work / "request.json"
                out_path = work / "result.json"
                images_dir = work / "images"
                images_dir.mkdir(parents=True, exist_ok=True)
                image_entries = []
                for index, png in enumerate(png_images):
                    image_path = images_dir / f"chart_{index + 1}.png"
                    image_path.write_bytes(png)
                    png_sha = sha256(png).hexdigest()
                    width, height = _png_dimensions(png)
                    image_entries.append({
                        "path": str(image_path),
                        "sha256": png_sha,
                        "width": width,
                        "height": height,
                    })
                bundle = {
                    "provider": self._authority.provider,
                    "model": self._authority.model,
                    "system": system_prompt,
                    "decision": decision_prompt,
                    "contextJson": json.dumps(context, ensure_ascii=False, sort_keys=True),
                    "images": image_entries,
                    "apiKeyEnv": self._api_key_env,
                }
                if self._base_url:
                    bundle["baseURL"] = self._base_url
                bundle_path.write_text(json.dumps(bundle), encoding="utf-8")

                tsx = self._harness_root / "node_modules" / ".bin" / "tsx.cmd"
                command = [
                    str(tsx),
                    str(self._bridge_script),
                    "--bundle", str(bundle_path),
                    "--out", str(out_path),
                ]
                completed = subprocess.run(
                    command,
                    cwd=str(self._harness_root),
                    capture_output=True,
                    text=True,
                    timeout=300,
                    check=False,
                )
                if not out_path.is_file():
                    tail = (completed.stdout or "")[-2000:] + (completed.stderr or "")[-2000:]
                    raise RuntimeError(f"provider-smoke bridge produced no result; {tail}")
                payload = json.loads(out_path.read_text(encoding="utf-8"))
                return SmokeBridgeResult(
                    status=str(payload.get("status", "ERROR")),
                    provider=str(payload.get("provider", self._authority.provider)),
                    model=str(payload.get("model", self._authority.model)),
                    raw_response_text=str(payload.get("raw_response_text", "")),
                    finish_reason=str(payload.get("finish_reason", "unknown")),
                    token_usage=dict(payload.get("token_usage") or {}),
                    provider_request_id=payload.get("provider_request_id"),
                    image_count=int(payload.get("image_count", 0)),
                    request_count=int(payload.get("request_count", 0)),
                    error=payload.get("error"),
                )
        finally:
            self._cleanup_bridge()

    @property
    def required_api_key_env(self) -> str:
        return self._api_key_env


class SmokeHarnessTransport:
    """Orchestrator transport that maps one governed wake to one Harness request.

    The runner precomputes one four-PNG image bundle per governed wake (in strict
    wake order).  Each ``execute(request)`` pops the next bundle, calls the
    one-shot Harness bridge exactly once, returns the raw response text, and
    records the bridge result (usage, provider request id, request count) for the
    evidence.  It never retries and never issues a second request.
    """

    provider_identity = "DEEPSEEK_HARNESS_ONE_SHOT_V0_1"
    mock = False

    def __init__(
        self,
        *,
        bridge: HarnessOneShotBridge,
        image_bundles: tuple[tuple[bytes, ...], ...],
        expected_provider: str,
        expected_model: str,
    ) -> None:
        # Duck-typed so tests can substitute a fake one-shot bridge; production
        # construction always uses a HarnessOneShotBridge (which itself enforces
        # the ACTIVE authority gate before any credential/network capability).
        if not callable(getattr(bridge, "execute", None)):
            raise TypeError("SmokeHarnessTransport requires a one-shot bridge with execute()")
        if len(image_bundles) != 3 or any(len(bundle) != 4 for bundle in image_bundles):
            raise ValueError("provider smoke transport requires exactly three four-PNG bundles")
        if not isinstance(expected_provider, str) or not expected_provider:
            raise ValueError("SmokeHarnessTransport requires the exact expected provider")
        if not isinstance(expected_model, str) or not expected_model:
            raise ValueError("SmokeHarnessTransport requires the exact expected model")
        self._bridge = bridge
        self._bundles = list(image_bundles)
        self._expected_provider = expected_provider
        self._expected_model = expected_model
        self.calls: list[SmokeBridgeResult] = []

    @property
    def provider_admitted(self) -> bool:
        return True

    @property
    def last_response_metadata(self) -> dict[str, object]:
        """Non-secret provider/billing metadata of the most recent bridge call."""
        if not self.calls:
            return {}
        result = self.calls[-1]
        return {
            "provider": result.provider,
            "model": result.model,
            "finish_reason": result.finish_reason,
            "provider_request_id": result.provider_request_id,
            "token_usage": dict(result.token_usage),
            "status": result.status,
        }

    def execute(self, request: Any) -> str:
        if not self._bundles:
            raise RuntimeError("provider smoke transport exhausted; a fourth request is forbidden")
        png_images = self._bundles.pop(0)
        result = self._bridge.execute(
            system_prompt=request.system_prompt,
            decision_prompt=request.decision_prompt,
            context=request.context,
            png_images=png_images,
        )
        self.calls.append(result)
        if result.status != "OK" or result.error:
            raise RuntimeError(f"provider smoke bridge failed closed: {result.error}")
        # Post-call fail-closed: exact provider/model, exactly four images, exactly one request.
        if result.provider != self._expected_provider:
            raise RuntimeError(
                f"provider smoke bridge returned unexpected provider {result.provider!r}; "
                f"expected {self._expected_provider!r}"
            )
        if result.model != self._expected_model:
            raise RuntimeError(
                f"provider smoke bridge returned unexpected model {result.model!r}; "
                f"expected {self._expected_model!r}"
            )
        if result.image_count != 4:
            raise RuntimeError(
                f"provider smoke bridge must attach exactly 4 images; got {result.image_count}"
            )
        if result.request_count != 1:
            raise RuntimeError(
                f"provider smoke bridge must make exactly 1 request; got {result.request_count}"
            )
        return result.raw_response_text


class SmokeDeterministicTransport:
    """Zero-cost deterministic mock transport for the smoke runner and tests."""

    provider_identity = PROVIDER_SMOKE_MOCK_IDENTITY
    mock = True

    def __init__(self, *, provider_admitted: bool = False) -> None:
        self.provider_admitted = provider_admitted
        self.calls: list[Any] = []
        self.last_response_metadata: dict[str, object] = {}

    def execute(self, request: Any) -> str:
        self.calls.append(request)
        return _valid_mock_response()


def _png_dimensions(png_bytes: bytes) -> tuple[int, int]:
    if not png_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("provider smoke image is not a PNG byte stream")
    if len(png_bytes) < 33:
        raise ValueError("provider smoke PNG is truncated")
    width = int.from_bytes(png_bytes[16:20], "big")
    height = int.from_bytes(png_bytes[20:24], "big")
    return width, height


__all__ = [
    "PROVIDER_SMOKE_MOCK_IDENTITY",
    "SMOKE_BRIDGE_VERSION",
    "HarnessOneShotBridge",
    "SmokeBridgeResult",
    "SmokeDeterministicTransport",
    "SmokeHarnessTransport",
    "_valid_mock_response",
]

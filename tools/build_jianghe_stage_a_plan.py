#!/usr/bin/env python3
"""Build/check the frozen non-outcome Jianghe Stage-A qualification plan.

This tool is deterministic and offline. It never resolves provider credentials and
never makes network requests. It binds the Owner-approved input protocol, current
paid-call authorization bytes, prompt package, synthetic bar recipe, renderer and
all three provider payload/budget reservations before the first billable call.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Mapping

ROOT_BOOTSTRAP = Path(__file__).resolve().parents[1]
if str(ROOT_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(ROOT_BOOTSTRAP))

from src.jianghe_prespend_runtime import (  # noqa: E402
    IMPLEMENTATION_TARGET_SPECS,
    PAID_CALL_AUTHORITY_PATH,
    load_current_repository_rate_card,
)
from src.jianghe_source_only_verification import (  # noqa: E402
    ROOT as REPOSITORY_ROOT,
    _repository_blob_bytes,
)
from src.jianghe_stage_a_runtime import (  # noqa: E402
    ALL_TRACKS,
    QUALIFICATION_FIXTURE_ID,
    STAGE_A_MAX_CALLS_PER_PROVIDER,
    STAGE_A_PLAN_VERSION,
    STAGE_A_PROTOCOL_VERSION,
    STAGE_A_PROVIDER_CAP_CNY,
    STAGE_A_STIMULUS_VERSION,
    STAGE_A_TOTAL_CAP_CNY,
    STAGE_A_REQUEST_VERSION_V0_1,
    StageAProviderTransport,
    build_stage_a_stimulus,
    exact_invocation_bounds,
    make_stage_a_request,
    qualification_visible_information,
    runtime_response_json_schema,
)


PLAN_AS_OF = datetime(2026, 8, 24, 1, 3, tzinfo=timezone.utc)  # Owner approval 09:03 +08
MAX_OUTPUT_TOKENS = 400
REQUEST_CONTRACT_VERSION = STAGE_A_REQUEST_VERSION_V0_1
PROMPT_PACKAGE_PATH = (
    REPOSITORY_ROOT / "docs" / "research" / "jianghe" / "JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_1.json"
)
PROTOCOL_AUTHORITY_PATH = (
    REPOSITORY_ROOT / "docs" / "reviews" / "JIANGHE_STAGE_A_INPUT_AND_VISUAL_STIMULUS_PROTOCOL_OWNER_DECISION_V0_1.md"
)
DEFAULT_OUTPUT = REPOSITORY_ROOT / "docs" / "evidence" / "JIANGHE_STAGE_A_FROZEN_PLAN_V0_1.json"


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _pretty(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"


def _load_prompt_package() -> tuple[Mapping[str, object], str]:
    blob = _repository_blob_bytes(PROMPT_PACKAGE_PATH)
    payload = json.loads(blob.decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("prompt package must be an object")
    required = {"system_prompt", "decision_prompt", "identities"}
    if not required.issubset(payload):
        raise ValueError("prompt package is missing governed fields")
    return payload, sha256(blob).hexdigest()


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _fine_bar_rows(stimulus) -> list[dict[str, object]]:
    bars = [bar for bar in stimulus.observation.bars if bar.timeframe == "5m"]
    bars.sort(key=lambda item: item.open_time)
    return [
        {
            "open_time": item.open_time.isoformat(),
            "close_time": item.close_time.isoformat(),
            "available_at": item.available_at.isoformat(),
            "open": item.open_price,
            "high": item.high_price,
            "low": item.low_price,
            "close": item.close_price,
            "volume": item.volume,
            "is_closed": item.is_closed,
        }
        for item in bars
    ]


def _inference_identity(spec, payload: Mapping[str, object]) -> str:
    provider_specific: dict[str, object] = {
        "provider_spec_identity": spec.identity,
        "model_id": spec.model_id,
        "payload_style": spec.payload_style,
        "tools": payload.get("tools"),
        "max_output_tokens": MAX_OUTPUT_TOKENS,
    }
    for name in ("thinking", "reasoning_effort", "reasoning_split", "response_format", "stream"):
        if name in payload:
            provider_specific[name] = payload[name]
    return _hash(provider_specific)


def build_plan() -> dict[str, object]:
    prompt_package, prompt_package_blob_sha256 = _load_prompt_package()
    protocol_blob = _repository_blob_bytes(PROTOCOL_AUTHORITY_PATH)
    paid_auth_blob = _repository_blob_bytes(PAID_CALL_AUTHORITY_PATH)
    visible = qualification_visible_information()
    stimulus = build_stage_a_stimulus()
    system_prompt = prompt_package["system_prompt"]
    decision_prompt = prompt_package["decision_prompt"]
    if not isinstance(system_prompt, str) or not isinstance(decision_prompt, str):
        raise ValueError("governed prompt strings are malformed")

    shared_requests = {
        track.value: make_stage_a_request(
            track,
            system_prompt=system_prompt,
            decision_prompt=decision_prompt,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            stimulus=stimulus,
            contract_version=REQUEST_CONTRACT_VERSION,
        )
        for track in ALL_TRACKS
    }

    providers: list[dict[str, object]] = []
    for spec in IMPLEMENTATION_TARGET_SPECS:
        transport = StageAProviderTransport(spec)
        rate_card = load_current_repository_rate_card(spec, now=PLAN_AS_OF)
        slots: list[dict[str, object]] = []
        provider_worst_case = Decimal("0")
        for index, track in enumerate(ALL_TRACKS, start=1):
            request = shared_requests[track.value]
            payload = transport.build_payload(request)
            payload_bytes = transport.payload_bytes(request)
            bounds = exact_invocation_bounds(transport, request, rate_card=rate_card)
            worst_case = StageAProviderTransport._worst_case_cny(rate_card, bounds)
            provider_worst_case += worst_case
            slots.append(
                {
                    "slot": index,
                    "track": track.value,
                    "fixture_id": QUALIFICATION_FIXTURE_ID,
                    "request_identity": request.identity,
                    "payload_sha256": sha256(payload_bytes).hexdigest(),
                    "inference_configuration_identity": _inference_identity(spec, payload),
                    "transmitted_structured_observation_identity": request.transmitted_structured_identity,
                    "transmitted_visual_identities": [item.identity for item in request.visuals],
                    "bounds": {
                        "max_text_input_tokens": bounds.max_text_input_tokens,
                        "max_image_tokens": bounds.max_image_tokens,
                        "max_output_tokens": bounds.max_output_tokens,
                        "transport_retries": bounds.transport_retries,
                    },
                    "worst_case_cny": _decimal_text(worst_case),
                }
            )
        if provider_worst_case > STAGE_A_PROVIDER_CAP_CNY:
            raise ValueError(
                f"{spec.provider_id} five-slot worst-case {provider_worst_case} exceeds frozen CNY6 cap"
            )
        providers.append(
            {
                "provider_id": spec.provider_id,
                "model_id": spec.model_id,
                "provider_spec_identity": spec.identity,
                "endpoint": spec.endpoint,
                "payload_style": spec.payload_style,
                "rate_card_identity": rate_card.identity,
                "pricing_authority_identity": rate_card.repository_authority_identity,
                "five_slot_worst_case_cny": _decimal_text(provider_worst_case),
                "provider_stage_a_cap_cny": _decimal_text(STAGE_A_PROVIDER_CAP_CNY),
                "slots": slots,
            }
        )

    visible_sha = sha256(_canonical_json(visible).encode("utf-8")).hexdigest()
    plan: dict[str, object] = {
        "artifact_schema_version": STAGE_A_PLAN_VERSION,
        "status": "FROZEN_BEFORE_FIRST_PAID_CALL",
        "plan_as_of": PLAN_AS_OF.isoformat(),
        "protocol_version": STAGE_A_PROTOCOL_VERSION,
        "stimulus_version": STAGE_A_STIMULUS_VERSION,
        "owner_protocol_authority_sha256": sha256(protocol_blob).hexdigest(),
        "paid_call_authorization_sha256": sha256(paid_auth_blob).hexdigest(),
        "qualification_fixture_id": QUALIFICATION_FIXTURE_ID,
        "visible_information_sha256": visible_sha,
        "prompt_package_blob_sha256": prompt_package_blob_sha256,
        "prompt_identities": prompt_package["identities"],
        "runtime_response_json_schema_identity": _hash(runtime_response_json_schema()),
        "stimulus": {
            "recipe_identity": stimulus.recipe_identity,
            "stimulus_identity": stimulus.identity,
            "observation_identity": stimulus.observation.identity.identity,
            "structured_observation_identity": stimulus.structured.identity,
            "visual_input_identity": stimulus.visual.identity,
            "png_sha256": stimulus.png_sha256,
            "renderer_config_identity": stimulus.renderer_config_identity,
            "renderer_input_identity": stimulus.renderer_input_identity,
            "renderer_visual_artifact_identity": stimulus.visual_artifact_identity,
            "synthetic_product": stimulus.observation.identity.product,
            "synthetic_contract": stimulus.observation.identity.concrete_contract,
            "fine_5m_bars": _fine_bar_rows(stimulus),
            "aggregation": {"15m_group_size": 3, "1H_group_size": 12},
        },
        "track_order": [track.value for track in ALL_TRACKS],
        "max_calls_per_provider": STAGE_A_MAX_CALLS_PER_PROVIDER,
        "max_output_tokens_per_call": MAX_OUTPUT_TOKENS,
        "stage_a_total_cap_cny": _decimal_text(STAGE_A_TOTAL_CAP_CNY),
        "stage_a_provider_cap_cny": _decimal_text(STAGE_A_PROVIDER_CAP_CNY),
        "project_shared_hard_cap_cny": "100",
        "automatic_retry": "FORBIDDEN",
        "provider_tools": "DISABLED",
        "outcome_access": "NO",
        "providers": providers,
    }
    plan["plan_identity"] = _hash(plan)
    return plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = _pretty(build_plan())
    if args.check:
        if not args.output.exists():
            raise SystemExit(f"frozen plan is missing: {args.output}")
        actual = args.output.read_text(encoding="utf-8")
        if actual != expected:
            raise SystemExit("frozen Stage-A plan differs from deterministic rebuild")
        print("STAGE_A_FROZEN_PLAN_CHECK=PASS")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(expected, encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

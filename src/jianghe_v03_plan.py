"""Deterministic V0.3 capability-first Stage-A frozen plan builder.

The plan freezes the provider-neutral common-exam identity, three provider inference
configs, three V0.3 attempt/slot identities, the shared capability-answer contract,
per-provider conservative worst-case reservations, the historical 0.270021 CNY
carry-forward and the CNY100 project hard cap. It never calls a provider.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json

from src.jianghe_prespend_runtime import (
    HARD_PROJECT_CAP_CNY,
    DEEPSEEK_VISION_SPEC,
    KIMI_K3_SPEC,
    MINIMAX_M3_SPEC,
    ProviderSpec,
    SelectedJiangheContextArtifact,
    load_current_repository_rate_card,
)
from src.jianghe_source_only_verification import (
    ROOT as REPOSITORY_ROOT,
    _repository_blob_bytes,
)
from src.jianghe_stage_a_frozen_stimulus import build_frozen_stage_a_stimulus
from src.jianghe_v03_runtime import (
    HISTORICAL_DEEPSEEK_CNY,
    HISTORICAL_KIMI_CNY,
    HISTORICAL_MINIMAX_CNY,
    HISTORICAL_PROJECT_ACCOUNTED_CNY,
    V03_EXECUTION_ORDER,
    V03_PROVIDER_CONFIGS,
    V03_PROTOCOL_VERSION,
    V03_QUALIFICATION_FIXTURE_ID,
    V03_REMOTE_REF,
    V03AttemptIdentity,
    V03CommonExamIdentity,
    V03ProviderInferenceConfig,
    V03ProviderTransport,
    V03Request,
    v03_capability_answer_contract_payload,
    v03_slot_identity,
)

V03_PLAN_VERSION = "JIANGHE_STAGE_A_FROZEN_PLAN_V0_3"
PLAN_AS_OF = datetime(2026, 8, 25, 0, 0, tzinfo=timezone.utc)
V03_PROMPT_PACKAGE_PATH = (
    REPOSITORY_ROOT / "docs" / "research" / "jianghe" / "JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_3.json"
)
OWNER_DECISION_PATH = (
    REPOSITORY_ROOT / "docs" / "reviews" / "JIANGHE_STAGE_A_V0_3_CAPABILITY_FIRST_OWNER_DECISION.md"
)
PRICING_AUTHORITY_PATH = (
    REPOSITORY_ROOT / "docs" / "evidence" / "JIANGHE_PROVIDER_PRICING_AUTHORITY_V0_1.json"
)
DEFAULT_OUTPUT = REPOSITORY_ROOT / "docs" / "evidence" / "JIANGHE_STAGE_A_FROZEN_PLAN_V0_3.json"

_SPEC_BY_PROVIDER: dict[str, ProviderSpec] = {
    spec.provider_id: spec for spec in (KIMI_K3_SPEC, DEEPSEEK_VISION_SPEC, MINIMAX_M3_SPEC)
}


def _canonical_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _load_prompt_package() -> tuple[dict[str, object], str]:
    blob = _repository_blob_bytes(V03_PROMPT_PACKAGE_PATH)
    payload = json.loads(blob.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("prompt package must be an object")
    required = {"system_prompt", "decision_prompt", "capability_answer_contract"}
    if not required.issubset(payload):
        raise ValueError("prompt package is missing governed fields")
    return payload, sha256(blob).hexdigest()


def _common_exam(
    stimulus,
    context,
    system_prompt: str,
    decision_prompt: str,
) -> V03CommonExamIdentity:
    return V03CommonExamIdentity(
        fixture_id=V03_QUALIFICATION_FIXTURE_ID,
        stimulus_identity=stimulus.identity,
        source_observation_identity=stimulus.observation.identity.identity,
        point_in_time=stimulus.observation.identity.decision_time.isoformat(),
        system_prompt_sha256=sha256(system_prompt.encode("utf-8")).hexdigest(),
        decision_prompt_sha256=sha256(decision_prompt.encode("utf-8")).hexdigest(),
        capability_answer_contract_identity=_hash(v03_capability_answer_contract_payload()),
        selected_context_identity=context.identity,
        model_context_identity=context.model_payload()["model_context_identity"],
        structured_observation_identity=stimulus.structured.identity,
        png_sha256=stimulus.png_sha256,
        visual_artifact_identity=stimulus.visual_artifact_identity,
        renderer_config_identity=stimulus.renderer_config_identity,
    )


def _provider_slot(
    config: V03ProviderInferenceConfig,
    common_exam: V03CommonExamIdentity,
    transport: V03ProviderTransport,
    stimulus,
    context,
    spec: ProviderSpec,
    now: datetime,
) -> dict[str, object]:
    rate_card = load_current_repository_rate_card(spec, now=now)
    attempt = V03AttemptIdentity(
        common_exam_identity=common_exam.identity,
        provider_inference_config_identity=config.identity,
        slot_identity=v03_slot_identity(config.provider_id),
        model_request_at=now.isoformat(),
    )
    request = V03Request(
        system_prompt="placeholder-system",
        decision_prompt="placeholder-decision",
        context=context,
        structured_observation=stimulus.structured,
        visual=stimulus.visual,
        common_exam_identity=common_exam,
        provider_config=config,
        attempt_identity=attempt,
        point_in_time=stimulus.observation.identity.decision_time.isoformat(),
    )
    payload_bytes = transport.payload_bytes(request)
    text_bound = transport.conservative_text_input_token_bound(request)
    if rate_card.image_billing_mode == "FIXED_INPUT_TOKENS_PER_IMAGE":
        image_bound = int(rate_card.fixed_input_tokens_per_image or 0)
    elif rate_card.image_billing_mode == "INPUT_TOKENS":
        image_bound = 0
    else:
        raise ValueError("unknown image billing mode")
    worst_case = (
        Decimal(text_bound + image_bound) * rate_card.input_per_million
        + Decimal(config.max_output_tokens) * rate_card.output_per_million
    ) / Decimal(1_000_000)
    return {
        "provider_id": config.provider_id,
        "model_id": config.model_id,
        "endpoint": config.endpoint,
        "api_key_env": config.api_key_env,
        "payload_style": config.payload_style,
        "provider_spec_identity": spec.identity,
        "provider_inference_config_identity": config.identity,
        "slot_identity": v03_slot_identity(config.provider_id),
        "attempt_identity": attempt.identity,
        "max_output_tokens": config.max_output_tokens,
        "network_timeout_seconds": config.network_timeout_seconds,
        "stream": config.stream,
        "tools": list(config.tools),
        "response_format_policy": config.response_format_policy,
        "image_wire_syntax": config.image_wire_syntax,
        "rate_card_identity": rate_card.identity,
        "text_input_bound_tokens": text_bound,
        "image_input_bound_tokens": image_bound,
        "worst_case_reservation_cny": _decimal_text(worst_case),
        "payload_sha256": sha256(payload_bytes).hexdigest(),
    }


def build_v03_frozen_plan() -> dict[str, object]:
    prompt_package, prompt_package_blob_sha256 = _load_prompt_package()
    system_prompt = prompt_package["system_prompt"]
    decision_prompt = prompt_package["decision_prompt"]
    if not isinstance(system_prompt, str) or not isinstance(decision_prompt, str):
        raise ValueError("governed prompt strings are malformed")
    owner_blob = _repository_blob_bytes(OWNER_DECISION_PATH)
    pricing_blob = _repository_blob_bytes(PRICING_AUTHORITY_PATH)
    stimulus = build_frozen_stage_a_stimulus()
    context = SelectedJiangheContextArtifact.from_fixture_id(V03_QUALIFICATION_FIXTURE_ID)
    common_exam = _common_exam(stimulus, context, system_prompt, decision_prompt)

    providers: list[dict[str, object]] = []
    total_worst = Decimal("0")
    for config in V03_PROVIDER_CONFIGS:
        if config.provider_id not in V03_EXECUTION_ORDER:
            raise ValueError("provider outside V0.3 execution order")
        spec = _SPEC_BY_PROVIDER[config.provider_id]
        transport = V03ProviderTransport(config)
        slot = _provider_slot(config, common_exam, transport, stimulus, context, spec, PLAN_AS_OF)
        providers.append(slot)
        total_worst += Decimal(slot["worst_case_reservation_cny"])

    plan: dict[str, object] = {
        "artifact_schema_version": V03_PLAN_VERSION,
        "status": "FROZEN_V0_3_OFFLINE__AWAITING_REVIEW",
        "plan_as_of": PLAN_AS_OF.isoformat(),
        "protocol_version": V03_PROTOCOL_VERSION,
        "owner_decision_authority_sha256": sha256(owner_blob).hexdigest(),
        "provider_pricing_authority_sha256": sha256(pricing_blob).hexdigest(),
        "prompt_package_blob_sha256": prompt_package_blob_sha256,
        "prompt_identities": {
            "system_prompt_sha256": sha256(system_prompt.encode("utf-8")).hexdigest(),
            "decision_prompt_sha256": sha256(decision_prompt.encode("utf-8")).hexdigest(),
            "capability_answer_contract_identity": _hash(
                v03_capability_answer_contract_payload()
            ),
        },
        "fixture_id": V03_QUALIFICATION_FIXTURE_ID,
        "common_exam_identity": common_exam.identity,
        "common_exam": {
            "fixture_id": V03_QUALIFICATION_FIXTURE_ID,
            "stimulus_identity": stimulus.identity,
            "observation_identity": stimulus.observation.identity.identity,
            "structured_observation_identity": stimulus.structured.identity,
            "visual_input_identity": stimulus.visual.identity,
            "png_sha256": stimulus.png_sha256,
            "visual_artifact_identity": stimulus.visual_artifact_identity,
            "renderer_config_identity": stimulus.renderer_config_identity,
            "selected_context_identity": context.identity,
            "model_context_identity": context.model_payload()["model_context_identity"],
            "point_in_time": stimulus.observation.identity.decision_time.isoformat(),
            "outcome_future_ban": True,
            "tools_search_ban": True,
            "production_json_ban": True,
        },
        "capability_answer_contract": v03_capability_answer_contract_payload(),
        "providers": providers,
        "execution_order": list(V03_EXECUTION_ORDER),
        "max_output_tokens_per_call": 131072,
        "network_timeout_seconds": 900,
        "historical_project_accounted_cny": _decimal_text(HISTORICAL_PROJECT_ACCOUNTED_CNY),
        "historical_breakdown_cny": {
            "DEEPSEEK": _decimal_text(HISTORICAL_DEEPSEEK_CNY),
            "MINIMAX": _decimal_text(HISTORICAL_MINIMAX_CNY),
            "KIMI": _decimal_text(HISTORICAL_KIMI_CNY),
        },
        "hard_project_cap_cny": _decimal_text(HARD_PROJECT_CAP_CNY),
        "total_worst_case_including_historical_cny": _decimal_text(
            HISTORICAL_PROJECT_ACCOUNTED_CNY + total_worst
        ),
        "theoretical_max_remaining_cny": _decimal_text(
            HARD_PROJECT_CAP_CNY - HISTORICAL_PROJECT_ACCOUNTED_CNY
        ),
        "automatic_retry": "FORBIDDEN",
        "provider_tools": "DISABLED",
        "outcome_access": "NO",
        "remote_ref": V03_REMOTE_REF,
        "caller_selected_remote_ref": "FORBIDDEN",
    }
    if total_worst <= 0 or HISTORICAL_PROJECT_ACCOUNTED_CNY + total_worst > HARD_PROJECT_CAP_CNY:
        raise ValueError("V0.3 worst-case reservations exceed the CNY100 hard cap")
    plan["plan_identity"] = _hash(plan)
    return plan


def pretty_plan_bytes(plan: dict[str, object]) -> bytes:
    return (
        json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")


__all__ = [
    "DEFAULT_OUTPUT", "PLAN_AS_OF", "V03_PLAN_VERSION", "build_v03_frozen_plan",
    "pretty_plan_bytes",
]

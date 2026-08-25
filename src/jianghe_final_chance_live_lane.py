"""V0.2 Jianghe downloaded-Kline Final-Chance single-slot live execution lane.

This module is the only Final-Chance V0.2 spend-eligible execution surface. It is
deliberately single-slot: one provider x one frozen case x one explicit
frozen attempt/slot per invocation. It reuses the repository-verified V0.3
provider transport / budget ledger / capability adapter and the provider-neutral
canonical artifacts, and it adds the V0.2 fail-closed gates required before any
network attempt:

* A: materialized plan identity + plan-file SHA-256 must equal the frozen authority;
* B: the requested case identity must exist in the frozen materialized plan;
* C: provider/model must equal the frozen slot provider/model;
* D: payload / image / prompt / structured-artifact identities must equal the plan;
* E: a formal explicit-slot authority is required (``NEXT_EXPLICIT_PAID_SLOT`` must
  not be ``NONE``); an API key / balance / paid authorization / materialized plan
  alone never lets the runner invent an executable slot;
* F: an already-successful attempt must not be re-executed (default fail-closed);
* G: network timeout / HTTP failure / malformed JSON record failure evidence and
  stop; automatic retry and automatic next-slot progression are forbidden.

This module never invents research semantics and never unlocks outcome / future /
validation / holdout / shadow / broker / real-money lanes. A real provider call is
only reachable when the caller injects a real HTTP seam and a matching repository
Owner authorization plus an explicit frozen slot authority.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import os
import re
import subprocess
from typing import Callable, Mapping, Protocol, Sequence
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

from src.jianghe_ai_trader import JiangheObservation, ObservationBar, ObservationIdentity
from src.jianghe_downloaded_kline_final_chance import (
    CONTEXT_FIXTURE_ID,
    DECISION_PROMPT_ADDENDUM,
    FOUR_HOUR_AGGREGATION_VERSION,
    HIGHER_TIMEFRAME_DESCRIPTOR_VERSION,
    HIGHER_WINDOW_COUNTS,
    LOWER_AGGREGATION_VERSION,
    LOWER_WINDOW_COUNTS,
    PANEL_ORDER,
    PILOT_ID,
    PLAN_VERSION,
    PROVIDER_ORDER,
    SAMPLE_COUNT,
    bar_payload,
    identity as final_chance_identity,
    verify_plan_spec,
)
from src.jianghe_downloaded_kline_input_contract import DownloadedKlineInputContractV02
from src.jianghe_prespend_runtime import (
    HARD_PROJECT_CAP_CNY,
    CanonicalStructuredObservationArtifact,
    DEEPSEEK_VISION_SPEC,
    KIMI_K3_SPEC,
    MINIMAX_M3_SPEC,
    PaidCallNotAuthorizedError,
    ProviderSpec,
    SelectedJiangheContextArtifact,
    VisualInputArtifact,
    load_current_repository_rate_card,
    load_owner_paid_call_authorization,
)
from src.jianghe_source_only_verification import (
    ROOT as REPOSITORY_ROOT,
    _repository_blob_bytes,
)
from src.jianghe_stage_a_frozen_stimulus import frozen_stage_a_renderer_config
from src.jianghe_v03_runtime import (
    V03BudgetLedger,
    V03CapabilityAdapter,
    V03InvocationEvidence,
    V03ModelMismatchError,
    V03ProviderInferenceConfig,
    V03ProviderTransport,
    V03Request,
    V03TerminalStatus,
    V03_PROVIDER_CONFIGS,
    v03_capability_answer_contract_identity,
)
from src.jianghe_visual_renderer import JiangheVisualRenderer, VisualObservationSpec, VisualPanel


# ---------------------------------------------------------------------------
# Frozen V0.2 authority identities (cross-checked against committed evidence)
# ---------------------------------------------------------------------------
PLAN_PATH = REPOSITORY_ROOT / "docs" / "evidence" / "JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_PLAN_V0_2.json"
PLAN_SPEC_PATH = (
    REPOSITORY_ROOT / "docs" / "evidence" / "JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_PLAN_SPEC_V0_2.json"
)
PROMPT_PACKAGE_PATH = (
    REPOSITORY_ROOT / "docs" / "research" / "jianghe" / "JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_3.json"
)
PILOT_PILOT_SUMMARY_PATH = (
    REPOSITORY_ROOT / "docs" / "evidence" / "JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_SUMMARY_V0_1.json"
)
SLOT_AUTHORITY_PATH = (
    REPOSITORY_ROOT / "docs" / "evidence"
    / "JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_EXPLICIT_SLOT_V0_2.json"
)
FINAL_CHANCE_REMOTE_REF = "refs/heads/final-chance-live-state-v0-2"
FINAL_CHANCE_LEDGER_FILENAME = "final-chance-live-ledger-v0-2.json"
FINAL_CHANCE_LEDGER_SCHEMA_VERSION = "JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_REMOTE_LEDGER_V0_1"
FINAL_CHANCE_LEDGER_EVENT_SCHEMA_VERSION = (
    "JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_REMOTE_LEDGER_EVENT_V0_1"
)
FINAL_CHANCE_SLOT_EVIDENCE_SCHEMA_VERSION = (
    "JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_SLOT_EVIDENCE_V0_1"
)
FINAL_CHANCE_SLOT_AUTHORITY_SCHEMA_VERSION = (
    "JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_EXPLICIT_SLOT_AUTHORITY_V0_1"
)

# Frozen authority values (also independently verified from committed files below).
PILOT_PLAN_IDENTITY = "34640cd6de7dd9f5069ad902e0e7c125b78aa7a5400475b4531ba318f3469340"
PLAN_FILE_SHA256 = "f72d16567b0f481551eda85cda3f5e67ba7c31a5504943e80e148540830cecbc"

# Shared project paid-research ledger carry-forward (authority: CURRENT_STATE.md /
# PROJECT_BRAIN_RUNTIME_BRIEF.md / PROJECT_HANDOFF_CURRENT.md and the committed V0.1
# pilot summary ``project_accounted_cny_after``).
FINAL_CHANCE_HISTORICAL_PROJECT_ACCOUNTED_CNY = Decimal("3.1609662")

NETWORK_ATTEMPT_STARTED = "NETWORK_ATTEMPT_STARTED"
ATTEMPT_TERMINAL = "ATTEMPT_TERMINAL"
NEXT_EXPLICIT_PAID_SLOT_NONE = "NONE"
MATERIALIZED_STATUS = "MATERIALIZED__AWAITING_PRESEND_REVIEW"

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_GIT_OID = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
_PROVIDER_CREDENTIAL_ENV_NAMES = frozenset(
    {"MOONSHOT_API_KEY", "DEEPSEEK_API_KEY", "MINIMAX_API_KEY"}
)
_SPEC_BY_PROVIDER: dict[str, ProviderSpec] = {
    spec.provider_id: spec for spec in (KIMI_K3_SPEC, DEEPSEEK_VISION_SPEC, MINIMAX_M3_SPEC)
}


class FinalChanceError(RuntimeError):
    """Base error for the V0.2 final-chance live lane."""


class FinalChancePlanError(FinalChanceError):
    pass


class FinalChanceGateError(FinalChanceError):
    """A fail-closed pre-send gate refused execution."""


class FinalChanceLedgerError(FinalChanceError):
    pass


class FinalChanceLedgerIntegrityError(FinalChanceLedgerError):
    pass


class FinalChanceLedgerConflictError(FinalChanceLedgerError):
    pass


class FinalChanceLedgerUnavailableError(FinalChanceLedgerError):
    pass


class FinalChanceLedgerVerificationError(FinalChanceLedgerError):
    pass


class FinalChanceSlotAuthorityError(FinalChanceError):
    pass


# ---------------------------------------------------------------------------
# Small deterministic helpers
# ---------------------------------------------------------------------------
def _canonical_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _hash_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


def _require_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be non-empty text")
    return value


def _require_sha256(value: object, name: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256")
    return value


def _require_aware(value: datetime, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


def _utc(value: datetime) -> str:
    return _require_aware(value, "datetime").astimezone(timezone.utc).isoformat(timespec="microseconds")


def _decimal(value: object, name: str, *, positive: bool = False) -> Decimal:
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{name} must be a finite Decimal") from None
    if not result.is_finite() or (positive and result <= 0) or (not positive and result < 0):
        raise ValueError(f"{name} must be a finite {'positive' if positive else 'non-negative'} Decimal")
    return result


def _decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


# ---------------------------------------------------------------------------
# 1. Plan loading / verification (gate A)
# ---------------------------------------------------------------------------
def _bar_from_payload(value: Mapping[str, object]) -> ObservationBar:
    return ObservationBar(
        timeframe=str(value["timeframe"]),
        open_time=datetime.fromisoformat(str(value["open_time"])),
        close_time=datetime.fromisoformat(str(value["close_time"])),
        available_at=datetime.fromisoformat(str(value["available_at"])),
        open_price=str(value["open_price"]),
        high_price=str(value["high_price"]),
        low_price=str(value["low_price"]),
        close_price=str(value["close_price"]),
        volume=str(value["volume"]),
        is_closed=value["is_closed"] is True,
    )


def _observation_from_sample(sample: Mapping[str, object]) -> JiangheObservation:
    decision_time = datetime.fromisoformat(str(sample["decision_time"]))
    return JiangheObservation(
        identity=ObservationIdentity(
            decision_time=decision_time,
            exchange_time=decision_time,
            product=str(sample["product"]),
            concrete_contract=str(sample["concrete_contract"]),
            mapping_identity=str(sample["mapping_identity"]),
            session_identity=str(sample["session_metadata_identity"]),
        ),
        bars=tuple(_bar_from_payload(item) for item in sample["visible_bars"]),
        visible_metadata=(("session", "UNKNOWN"),),
    )


def reconstruct_final_chance_artifacts(
    sample: Mapping[str, object],
) -> tuple[
    JiangheObservation,
    CanonicalStructuredObservationArtifact,
    VisualInputArtifact,
    dict[str, str],
]:
    """Deterministically rebuild the observation / structured / visual artifacts.

    This mirrors the committed materialization reconstruction exactly, so the
    returned artifact identities must equal the frozen plan payload identities.
    """
    observation = _observation_from_sample(sample)
    counts = {tf: sum(bar.timeframe == tf for bar in observation.bars) for tf in PANEL_ORDER}
    if counts != {**HIGHER_WINDOW_COUNTS, **LOWER_WINDOW_COUNTS}:
        raise FinalChancePlanError("timeframe counts drifted from the frozen plan")
    descriptors = sample.get("higher_timeframe_bar_descriptors")
    four_hour_bars = tuple(bar for bar in observation.bars if bar.timeframe == "4H")
    if not isinstance(descriptors, list) or len(descriptors) != len(four_hour_bars):
        raise FinalChancePlanError("4H descriptors missing from the frozen plan")
    for bar, descriptor in zip(four_hour_bars, descriptors):
        if descriptor.get("aggregation_version") != FOUR_HOUR_AGGREGATION_VERSION:
            raise FinalChancePlanError("4H descriptor version mismatch")
        if descriptor.get("official_trading_day") != sample.get("trading_day"):
            raise FinalChancePlanError("4H trading-day binding mismatch")
        if descriptor.get("observation_bar_identity") != final_chance_identity(bar_payload(bar)):
            raise FinalChancePlanError("4H descriptor visible-bar binding mismatch")
        if descriptor.get("volume_comparison_eligible") is not False:
            raise FinalChancePlanError("4H volume comparison must remain disabled")
        grid_start = datetime.fromisoformat(str(descriptor["grid_start"]))
        grid_end = datetime.fromisoformat(str(descriptor["grid_end"]))
        if not (grid_start <= bar.open_time < bar.close_time <= grid_end):
            raise FinalChancePlanError("4H bar outside its civil grid")

    structured = CanonicalStructuredObservationArtifact.from_observation(observation)
    lower = JiangheObservation(
        identity=ObservationIdentity(
            decision_time=observation.identity.decision_time,
            exchange_time=observation.identity.exchange_time,
            product=observation.identity.product,
            concrete_contract=observation.identity.concrete_contract,
            mapping_identity=str(sample["lower_projection_mapping_identity"]),
            session_identity=observation.identity.session_identity,
        ),
        bars=tuple(bar for bar in observation.bars if bar.timeframe != "4H"),
        visible_metadata=observation.visible_metadata,
    )
    lower_structured = CanonicalStructuredObservationArtifact.from_observation(lower)
    lower_contract = DownloadedKlineInputContractV02.from_observation(lower, lower_structured)
    higher_payload = {
        "version": HIGHER_TIMEFRAME_DESCRIPTOR_VERSION,
        "source_observation_identity": observation.identity.identity,
        "timeframe": "4H",
        "role": "BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY",
        "aggregation_version": FOUR_HOUR_AGGREGATION_VERSION,
        "cross_timeframe_volume_comparison_eligible": False,
        "bars": descriptors,
    }
    panels = tuple(
        VisualPanel(tf, tuple(bar for bar in observation.bars if bar.timeframe == tf))
        for tf in PANEL_ORDER
    )
    rendered = JiangheVisualRenderer(frozen_stage_a_renderer_config()).render(
        VisualObservationSpec(
            product=observation.identity.product,
            concrete_contract=observation.identity.concrete_contract,
            as_of=observation.identity.decision_time,
            panels=panels,
        )
    )
    visual = VisualInputArtifact(
        source_observation_identity=observation.identity.identity,
        renderer_identity=rendered.renderer_config_identity,
        png_bytes=rendered.png_bytes,
    )
    hashes = {
        "full_structured_observation_identity": structured.identity,
        "lower_input_contract_identity": lower_contract.identity,
        "higher_timeframe_descriptor_identity": final_chance_identity(higher_payload),
        "png_sha256": rendered.png_sha256,
        "renderer_config_identity": rendered.renderer_config_identity,
        "visual_artifact_identity": rendered.visual_artifact_identity,
        "visual_input_identity": visual.identity,
    }
    for name, value in hashes.items():
        if sample.get(name) != value:
            raise FinalChancePlanError(f"frozen sample {name} drifted")
    return observation, structured, visual, hashes


def verify_final_chance_plan(plan: Mapping[str, object]) -> str:
    """Fail-closed verification of the materialized plan (mirrors the committed tool)."""
    if plan.get("schema_version") != PLAN_VERSION:
        raise FinalChancePlanError("plan version mismatch")
    if plan.get("status") != MATERIALIZED_STATUS:
        raise FinalChancePlanError("materialized plan must remain fail-closed")
    if plan.get("next_explicit_paid_slot") is not None:
        raise FinalChancePlanError("materialized plan cannot create a paid slot")
    if plan.get("pilot_id") != PILOT_ID:
        raise FinalChancePlanError("plan pilot id mismatch")
    samples = plan.get("samples")
    slots = plan.get("provider_slots")
    if not isinstance(samples, list) or len(samples) != SAMPLE_COUNT:
        raise FinalChancePlanError("materialized plan requires four samples")
    if not isinstance(slots, list) or len(slots) != SAMPLE_COUNT * len(PROVIDER_ORDER):
        raise FinalChancePlanError("materialized plan requires 12 non-executable slots")
    if any(slot.get("execution_eligible") is not False for slot in slots):
        raise FinalChancePlanError("materialized slots must remain non-executable")
    for sample in samples:
        observation, structured, visual, hashes = reconstruct_final_chance_artifacts(sample)
        if sample.get("observation_identity") != observation.identity.identity:
            raise FinalChancePlanError("sample observation identity mismatch")
        if structured.identity != sample.get("full_structured_observation_identity"):
            raise FinalChancePlanError("sample structured identity mismatch")
        if visual.identity != sample.get("visual_input_identity"):
            raise FinalChancePlanError("sample visual input identity mismatch")
        if visual.content_sha256 != sample.get("png_sha256"):
            raise FinalChancePlanError("sample png identity mismatch")
        declared = sample.get("sample_identity")
        payload = dict(sample)
        payload.pop("sample_identity", None)
        if declared != final_chance_identity(payload):
            raise FinalChancePlanError("sample identity mismatch")
        del hashes
    payload = dict(plan)
    declared = payload.pop("pilot_plan_identity", None)
    calculated = final_chance_identity(payload)
    if declared != calculated:
        raise FinalChancePlanError("plan identity mismatch")
    if declared != PILOT_PLAN_IDENTITY:
        raise FinalChancePlanError("plan identity differs from the frozen authority")
    return str(declared)


def committed_plan_file_sha256(plan_bytes: bytes | None = None) -> str:
    """SHA-256 of the exact committed materialized-plan file bytes."""
    if plan_bytes is None:
        plan_bytes = _repository_blob_bytes(PLAN_PATH)
    return _hash_bytes(plan_bytes)


def load_verified_final_chance_plan(
    *, plan_bytes: bytes | None = None, spec_bytes: bytes | None = None
) -> dict[str, object]:
    """Load and verify the only production final-chance materialized plan.

    ``plan_bytes`` / ``spec_bytes`` are injectable for tests; the production default
    reads the committed evidence blobs and verifies the frozen file SHA-256.
    """
    if plan_bytes is None:
        plan_bytes = _repository_blob_bytes(PLAN_PATH)
    if _hash_bytes(plan_bytes) != PLAN_FILE_SHA256:
        raise FinalChancePlanError("plan file SHA-256 differs from the frozen authority")
    try:
        plan = json.loads(plan_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise FinalChancePlanError("materialized plan is not valid UTF-8 JSON") from error
    if not isinstance(plan, Mapping):
        raise FinalChancePlanError("materialized plan must be an object")
    verify_final_chance_plan(plan)

    if spec_bytes is None:
        spec_bytes = _repository_blob_bytes(PLAN_SPEC_PATH)
    try:
        spec = json.loads(spec_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise FinalChancePlanError("plan spec is not valid UTF-8 JSON") from error
    if not isinstance(spec, Mapping):
        raise FinalChancePlanError("plan spec must be an object")
    verify_plan_spec(spec)
    if str(spec.get("plan_spec_identity")) != str(plan.get("plan_spec_identity")):
        raise FinalChancePlanError("plan is not bound to the committed plan spec")
    return dict(plan)


# ---------------------------------------------------------------------------
# 2. Prompt package + decision prompt (with 4H addendum)
# ---------------------------------------------------------------------------
def load_final_chance_prompt_package(
    *, package_bytes: bytes | None = None,
) -> tuple[str, str, str]:
    """Return ``(system_prompt, decision_prompt, addendum)`` verified against the plan."""
    if package_bytes is None:
        package_bytes = _repository_blob_bytes(PROMPT_PACKAGE_PATH)
    try:
        package = json.loads(package_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise FinalChancePlanError("prompt package is not valid UTF-8 JSON") from error
    if not isinstance(package, Mapping):
        raise FinalChancePlanError("prompt package must be an object")
    system_prompt = package.get("system_prompt")
    decision_prompt = package.get("decision_prompt")
    if not isinstance(system_prompt, str) or not isinstance(decision_prompt, str):
        raise FinalChancePlanError("prompt package is missing governed prompt strings")
    return system_prompt, decision_prompt, DECISION_PROMPT_ADDENDUM


def final_decision_prompt(decision_prompt: str, addendum: str) -> str:
    """Deterministic combination of the governed decision prompt and the 4H addendum."""
    if not isinstance(decision_prompt, str) or not isinstance(addendum, str):
        raise TypeError("decision prompt and addendum must be text")
    if addendum != DECISION_PROMPT_ADDENDUM:
        raise FinalChancePlanError("decision prompt addendum drifted")
    return f"{decision_prompt}\n\n{addendum}"


# ---------------------------------------------------------------------------
# 3. Request construction (gates B / C / D)
# ---------------------------------------------------------------------------
def _provider_config(plan: Mapping[str, object], provider_id: str) -> V03ProviderInferenceConfig:
    if provider_id not in PROVIDER_ORDER:
        raise FinalChanceGateError(f"unsupported final-chance provider {provider_id}")
    declared_model = None
    for entry in plan.get("provider_configs", []):
        if isinstance(entry, Mapping) and entry.get("provider_id") == provider_id:
            declared_model = str(entry.get("model_id"))
            break
    if declared_model is None:
        raise FinalChanceGateError(f"plan has no provider config for {provider_id}")
    matches = [config for config in V03_PROVIDER_CONFIGS if config.provider_id == provider_id]
    if len(matches) != 1:
        raise FinalChanceGateError(f"provider inference config for {provider_id} is ambiguous")
    config = matches[0]
    if config.model_id != declared_model:
        raise FinalChanceGateError("plan provider model differs from the frozen inference config")
    return config


def _plan_slot(plan: Mapping[str, object], provider_id: str, sample_id: str) -> dict[str, object]:
    for slot in plan.get("provider_slots", []):
        if isinstance(slot, Mapping) and slot.get("provider_id") == provider_id and slot.get("sample_id") == sample_id:
            return slot
    raise FinalChanceGateError(f"frozen plan has no slot for {provider_id}/{sample_id}")


def find_final_chance_slot_identity(
    plan: Mapping[str, object], provider_id: str, sample_id: str
) -> str:
    slot = _plan_slot(plan, provider_id, sample_id)
    return str(slot["slot_identity"])


def _common_case_binding(plan: Mapping[str, object], sample_id: str) -> dict[str, object]:
    for binding in plan.get("common_case_bindings", []):
        if isinstance(binding, Mapping) and binding.get("sample_id") == sample_id:
            return binding
    raise FinalChanceGateError(f"frozen plan has no common case binding for {sample_id}")


def build_final_chance_request(
    plan: Mapping[str, object],
    *,
    provider_id: str,
    sample_id: str,
    now: datetime,
) -> tuple[V03Request, V03ProviderTransport, V03ProviderInferenceConfig, dict[str, str]]:
    """Construct the exact single-slot request, verifying every identity (gates B/C/D)."""
    _require_aware(now, "now")
    sample = next((item for item in plan.get("samples", []) if item.get("sample_id") == sample_id), None)
    if sample is None:
        raise FinalChanceGateError(f"frozen plan has no sample {sample_id}")
    binding = _common_case_binding(plan, sample_id)
    config = _provider_config(plan, provider_id)
    slot = _plan_slot(plan, provider_id, sample_id)
    slot_identity = str(slot["slot_identity"])
    if slot.get("execution_eligible") is not False:
        raise FinalChanceGateError("materialized slot must remain non-executable until explicit authority")

    observation, structured, visual, _ = reconstruct_final_chance_artifacts(sample)
    system_prompt, decision_prompt, addendum = load_final_chance_prompt_package()
    if sha256(system_prompt.encode("utf-8")).hexdigest() != str(plan.get("system_prompt_sha256")):
        raise FinalChanceGateError("system prompt identity drifted from the plan")
    if sha256(decision_prompt.encode("utf-8")).hexdigest() != str(plan.get("decision_prompt_sha256")):
        raise FinalChanceGateError("decision prompt identity drifted from the plan")
    if sha256(addendum.encode("utf-8")).hexdigest() != str(plan.get("decision_prompt_addendum_sha256")):
        raise FinalChanceGateError("decision prompt addendum identity drifted from the plan")
    final_prompt = final_decision_prompt(decision_prompt, addendum)
    final_prompt_sha = sha256(final_prompt.encode("utf-8")).hexdigest()

    binding_payload = binding.get("payload", {})
    if (
        str(binding_payload.get("sample_identity")) != str(sample["sample_identity"])
        or str(binding_payload.get("full_structured_observation_identity")) != structured.identity
        or str(binding_payload.get("png_sha256")) != visual.content_sha256
        or str(binding_payload.get("system_prompt_sha256")) != str(plan["system_prompt_sha256"])
        or str(binding_payload.get("decision_prompt_sha256")) != str(plan["decision_prompt_sha256"])
        or str(binding_payload.get("decision_prompt_addendum_sha256"))
        != str(plan["decision_prompt_addendum_sha256"])
    ):
        raise FinalChanceGateError("common-case binding payload drifted from the plan")

    context = SelectedJiangheContextArtifact.from_fixture_id(CONTEXT_FIXTURE_ID)
    context_binding = plan.get("jianghe_context_binding", {})
    if (
        context.identity != context_binding.get("selected_context_identity")
        or context.model_payload()["model_context_identity"]
        != context_binding.get("model_context_identity")
        or context_binding.get("fixture_id") != CONTEXT_FIXTURE_ID
    ):
        raise FinalChanceGateError("selected Jianghe context drifted from the plan")

    common_exam = _build_common_exam(
        sample=sample,
        observation=observation,
        structured=structured,
        visual=visual,
        system_prompt_sha256=str(plan["system_prompt_sha256"]),
        decision_prompt_sha256=final_prompt_sha,
        context=context,
    )
    attempt = _build_attempt(common_exam, config, slot_identity, now)
    request = V03Request(
        system_prompt=system_prompt,
        decision_prompt=final_prompt,
        context=context,
        structured_observation=structured,
        visual=visual,
        common_exam_identity=common_exam,
        provider_config=config,
        attempt_identity=attempt,
        point_in_time=str(sample["decision_time"]),
    )
    transport = V03ProviderTransport(config)
    return request, transport, config, {
        "final_decision_prompt_sha256": final_prompt_sha,
        "sample_identity": str(sample["sample_identity"]),
        "case_identity": str(binding["common_case_identity"]),
        "source_observation_identity": observation.identity.identity,
    }


def _build_common_exam(
    *,
    sample: Mapping[str, object],
    observation: JiangheObservation,
    structured: CanonicalStructuredObservationArtifact,
    visual: VisualInputArtifact,
    system_prompt_sha256: str,
    decision_prompt_sha256: str,
    context: SelectedJiangheContextArtifact,
):
    from src.jianghe_v03_runtime import V03CommonExamIdentity

    return V03CommonExamIdentity(
        fixture_id=str(sample["sample_id"]),
        stimulus_identity=str(sample["sample_identity"]),
        source_observation_identity=observation.identity.identity,
        point_in_time=str(sample["decision_time"]),
        system_prompt_sha256=system_prompt_sha256,
        decision_prompt_sha256=decision_prompt_sha256,
        capability_answer_contract_identity=v03_capability_answer_contract_identity(),
        selected_context_identity=context.identity,
        model_context_identity=context.model_payload()["model_context_identity"],
        structured_observation_identity=structured.identity,
        png_sha256=visual.content_sha256,
        visual_artifact_identity=str(sample["visual_artifact_identity"]),
        renderer_config_identity=visual.renderer_identity,
    )


def _build_attempt(common_exam, config: V03ProviderInferenceConfig, slot_identity: str, now: datetime):
    from src.jianghe_v03_runtime import V03AttemptIdentity

    return V03AttemptIdentity(
        common_exam_identity=common_exam.identity,
        provider_inference_config_identity=config.identity,
        slot_identity=slot_identity,
        model_request_at=now.isoformat(),
    )


def image_input_bound(rate_card) -> int:
    if rate_card.image_billing_mode == "FIXED_INPUT_TOKENS_PER_IMAGE":
        return int(rate_card.fixed_input_tokens_per_image or 0)
    if rate_card.image_billing_mode == "INPUT_TOKENS":
        return 0
    raise FinalChanceGateError("unknown image billing mode fails closed")


def compute_final_chance_reservation(
    request: V03Request,
    transport: V03ProviderTransport,
    config: V03ProviderInferenceConfig,
    rate_card,
) -> tuple[Decimal, int]:
    text_bound = transport.conservative_text_input_token_bound(request)
    image_bound = image_input_bound(rate_card)
    worst = (
        Decimal(text_bound + image_bound) * rate_card.input_per_million
        + Decimal(config.max_output_tokens) * rate_card.output_per_million
    ) / Decimal("1000000")
    return worst, image_bound


def provider_spec_for(provider_id: str) -> ProviderSpec:
    spec = _SPEC_BY_PROVIDER.get(provider_id)
    if spec is None:
        raise FinalChanceGateError(f"unsupported final-chance provider {provider_id}")
    return spec


# ---------------------------------------------------------------------------
# 4. Explicit slot authority (gate E)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FinalChanceExplicitSlotAuthority:
    explicit_slot_identity: str
    plan_identity: str
    plan_file_sha256: str
    provider_id: str
    model_id: str
    sample_id: str
    case_identity: str
    authorization_id: str
    rate_card_identity: str
    worst_case_reservation_cny: str
    effective_at: datetime
    expires_at: datetime
    authority_identity: str

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> "FinalChanceExplicitSlotAuthority":
        required = frozenset({
            "artifact_schema_version", "next_explicit_paid_slot", "explicit_slot_identity",
            "plan_identity", "plan_file_sha256", "provider_id", "model_id", "sample_id",
            "case_identity", "authorization_id", "rate_card_identity",
            "worst_case_reservation_cny", "effective_at", "expires_at", "authority_identity",
        })
        if not isinstance(payload, Mapping) or set(payload) != required:
            raise FinalChanceSlotAuthorityError("explicit-slot authority schema is not closed-world")
        if payload.get("artifact_schema_version") != FINAL_CHANCE_SLOT_AUTHORITY_SCHEMA_VERSION:
            raise FinalChanceSlotAuthorityError("explicit-slot authority schema version is unknown")
        identity_payload = dict(payload)
        declared = identity_payload.pop("authority_identity")
        if _require_sha256(declared, "authority_identity") != _hash(identity_payload):
            raise FinalChanceSlotAuthorityError("explicit-slot authority identity does not match content")
        next_slot = payload.get("next_explicit_paid_slot")
        explicit = payload.get("explicit_slot_identity")
        if next_slot in (None, NEXT_EXPLICIT_PAID_SLOT_NONE) or explicit in (None, NEXT_EXPLICIT_PAID_SLOT_NONE):
            raise FinalChanceSlotAuthorityError("NEXT_EXPLICIT_PAID_SLOT is NONE")
        if next_slot != explicit:
            raise FinalChanceSlotAuthorityError("explicit-slot authority is internally inconsistent")
        try:
            effective_at = datetime.fromisoformat(str(payload["effective_at"]))
            expires_at = datetime.fromisoformat(str(payload["expires_at"]))
        except (KeyError, ValueError) as error:
            raise FinalChanceSlotAuthorityError("explicit-slot authority validity is malformed") from error
        return cls(
            explicit_slot_identity=_require_text(explicit, "explicit_slot_identity"),
            plan_identity=_require_sha256(payload.get("plan_identity"), "plan_identity"),
            plan_file_sha256=_require_sha256(payload.get("plan_file_sha256"), "plan_file_sha256"),
            provider_id=_require_text(payload.get("provider_id"), "provider_id"),
            model_id=_require_text(payload.get("model_id"), "model_id"),
            sample_id=_require_text(payload.get("sample_id"), "sample_id"),
            case_identity=_require_sha256(payload.get("case_identity"), "case_identity"),
            authorization_id=_require_text(payload.get("authorization_id"), "authorization_id"),
            rate_card_identity=_require_sha256(
                payload.get("rate_card_identity"), "rate_card_identity"
            ),
            worst_case_reservation_cny=_require_text(
                payload.get("worst_case_reservation_cny"), "worst_case_reservation_cny"
            ),
            effective_at=_require_aware(effective_at, "effective_at"),
            expires_at=_require_aware(expires_at, "expires_at"),
            authority_identity=declared,
        )

    def payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "artifact_schema_version": FINAL_CHANCE_SLOT_AUTHORITY_SCHEMA_VERSION,
            "next_explicit_paid_slot": self.explicit_slot_identity,
            "explicit_slot_identity": self.explicit_slot_identity,
            "plan_identity": self.plan_identity,
            "plan_file_sha256": self.plan_file_sha256,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "sample_id": self.sample_id,
            "case_identity": self.case_identity,
            "authorization_id": self.authorization_id,
            "rate_card_identity": self.rate_card_identity,
            "worst_case_reservation_cny": self.worst_case_reservation_cny,
            "effective_at": _utc(self.effective_at),
            "expires_at": _utc(self.expires_at),
        }
        payload["authority_identity"] = _hash(payload)
        return payload


def load_final_chance_explicit_slot_authority(
    *, read_bytes: Callable[[], bytes] | None = None
) -> FinalChanceExplicitSlotAuthority | None:
    """Load the committed explicit-slot authority. Absent file => ``None`` (slot NONE)."""
    reader = read_bytes or (lambda: _repository_blob_bytes(SLOT_AUTHORITY_PATH))
    try:
        blob = reader()
    except ValueError:
        return None
    try:
        payload = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise FinalChanceSlotAuthorityError("explicit-slot authority is malformed") from error
    return FinalChanceExplicitSlotAuthority.from_payload(payload)


# ---------------------------------------------------------------------------
# 5. Remote write-ahead ledger
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FinalChanceSnapshot:
    attempted_slots: frozenset[str]
    project_accounted_cny: Decimal
    total_attempts: int


class FinalChanceRemoteExecutionLedger:
    """Write-ahead execution ledger bound to the V0.2 plan and identities."""

    def __init__(
        self,
        plan_identity: str,
        plan_sha256: str,
        events: Sequence[Mapping[str, object]] = (),
        *,
        historical_accounted_cny: Decimal = FINAL_CHANCE_HISTORICAL_PROJECT_ACCOUNTED_CNY,
    ) -> None:
        _require_sha256(plan_identity, "plan_identity")
        _require_sha256(plan_sha256, "plan_sha256")
        self.plan_identity = plan_identity
        self.plan_sha256 = plan_sha256
        self.events = tuple(dict(event) for event in events)
        self.historical_accounted_cny = _decimal(
            historical_accounted_cny, "historical_accounted_cny"
        )
        self._validate_events()

    @classmethod
    def from_bytes(
        cls,
        plan_identity: str,
        plan_sha256: str,
        raw_bytes: bytes,
    ) -> "FinalChanceRemoteExecutionLedger":
        try:
            payload = json.loads(raw_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise FinalChanceLedgerIntegrityError("final-chance remote ledger is not valid JSON") from error
        if not isinstance(payload, dict) or frozenset(payload) != frozenset({
            "artifact_schema_version", "ledger_identity", "plan_identity",
            "plan_sha256", "events",
        }):
            raise FinalChanceLedgerIntegrityError("final-chance remote ledger top-level schema mismatch")
        if payload["artifact_schema_version"] != FINAL_CHANCE_LEDGER_SCHEMA_VERSION:
            raise FinalChanceLedgerIntegrityError("final-chance remote ledger schema version mismatch")
        if payload["plan_identity"] != plan_identity or payload["plan_sha256"] != plan_sha256:
            raise FinalChanceLedgerIntegrityError(
                "final-chance remote ledger is bound to a different frozen plan"
            )
        events = payload["events"]
        if not isinstance(events, list):
            raise FinalChanceLedgerIntegrityError("final-chance remote ledger events must be a list")
        identity_payload = dict(payload)
        declared = identity_payload.pop("ledger_identity")
        if _require_sha256(declared, "ledger_identity") != _hash(identity_payload):
            raise FinalChanceLedgerIntegrityError(
                "final-chance remote ledger identity does not match content"
            )
        return cls(plan_identity, plan_sha256, events)

    def payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "artifact_schema_version": FINAL_CHANCE_LEDGER_SCHEMA_VERSION,
            "ledger_identity": None,
            "plan_identity": self.plan_identity,
            "plan_sha256": self.plan_sha256,
            "events": [dict(event) for event in self.events],
        }
        identity_payload = dict(payload)
        identity_payload.pop("ledger_identity")
        payload["ledger_identity"] = _hash(identity_payload)
        return payload

    def to_bytes(self) -> bytes:
        return (_canonical_json(self.payload()) + "\n").encode("utf-8")

    def _new_event(
        self,
        *,
        now: datetime,
        event_type: str,
        provider_id: str,
        slot_identity: str,
        request_identity: str,
        worst_case_cny: Decimal,
        start_event_identity: str | None,
        status: str | None,
        accounted_cny: Decimal | None,
        evidence_identity: str | None,
    ) -> dict[str, object]:
        event: dict[str, object] = {
            "artifact_schema_version": FINAL_CHANCE_LEDGER_EVENT_SCHEMA_VERSION,
            "sequence": len(self.events) + 1,
            "event_type": event_type,
            "recorded_at": _utc(now),
            "prev_event_identity": None if not self.events else self.events[-1]["event_identity"],
            "plan_identity": self.plan_identity,
            "plan_sha256": self.plan_sha256,
            "provider_id": _require_text(provider_id, "provider_id"),
            "slot_identity": _require_text(slot_identity, "slot_identity"),
            "request_identity": _require_sha256(request_identity, "request_identity"),
            "worst_case_cny": _decimal_text(_decimal(worst_case_cny, "worst_case_cny", positive=True)),
            "start_event_identity": (
                None if start_event_identity is None
                else _require_sha256(start_event_identity, "start_event_identity")
            ),
            "status": status,
            "accounted_cny": (
                None if accounted_cny is None
                else _decimal_text(_decimal(accounted_cny, "accounted_cny"))
            ),
            "evidence_identity": (
                None if evidence_identity is None
                else _require_sha256(evidence_identity, "evidence_identity")
            ),
            "event_identity": None,
        }
        identity_payload = dict(event)
        identity_payload.pop("event_identity")
        event["event_identity"] = _hash(identity_payload)
        return event

    def _validate_events(self) -> None:
        starts: dict[str, str] = {}
        terminals: set[str] = set()
        previous: str | None = None
        for sequence, event in enumerate(self.events, start=1):
            expected = frozenset({
                "artifact_schema_version", "sequence", "event_type", "recorded_at",
                "prev_event_identity", "plan_identity", "plan_sha256", "provider_id",
                "slot_identity", "request_identity", "worst_case_cny",
                "start_event_identity", "status", "accounted_cny", "evidence_identity",
                "event_identity",
            })
            if frozenset(event) != expected:
                raise FinalChanceLedgerIntegrityError("final-chance remote event schema mismatch")
            if event["artifact_schema_version"] != FINAL_CHANCE_LEDGER_EVENT_SCHEMA_VERSION:
                raise FinalChanceLedgerIntegrityError("final-chance remote event version mismatch")
            if event["sequence"] != sequence or event["prev_event_identity"] != previous:
                raise FinalChanceLedgerIntegrityError(
                    "final-chance remote ledger sequence/hash chain is broken"
                )
            try:
                recorded_at = datetime.fromisoformat(str(event["recorded_at"]))
            except ValueError as error:
                raise FinalChanceLedgerIntegrityError("final-chance remote event timestamp is malformed") from error
            _require_aware(recorded_at, "recorded_at")
            declared = _require_sha256(event["event_identity"], "event_identity")
            identity_payload = dict(event)
            identity_payload.pop("event_identity")
            if declared != _hash(identity_payload):
                raise FinalChanceLedgerIntegrityError(
                    "final-chance remote event identity does not match content"
                )
            if event["plan_identity"] != self.plan_identity or event["plan_sha256"] != self.plan_sha256:
                raise FinalChanceLedgerIntegrityError(
                    "final-chance remote event frozen-plan binding mismatch"
                )
            slot = str(event["slot_identity"])
            if not slot.startswith("DKL_FC_V0_2:"):
                raise FinalChanceLedgerIntegrityError("final-chance remote event slot is not a V0.2 slot")
            if event["event_type"] == NETWORK_ATTEMPT_STARTED:
                if slot in starts:
                    raise FinalChanceLedgerIntegrityError("final-chance remote slot has duplicate start")
                if any(
                    event[name] is not None
                    for name in ("start_event_identity", "status", "accounted_cny", "evidence_identity")
                ):
                    raise FinalChanceLedgerIntegrityError("final-chance remote start contains terminal fields")
                starts[slot] = declared
            elif event["event_type"] == ATTEMPT_TERMINAL:
                if slot not in starts or slot in terminals:
                    raise FinalChanceLedgerIntegrityError(
                        "final-chance remote terminal has no unique start"
                    )
                if event["start_event_identity"] != starts[slot]:
                    raise FinalChanceLedgerIntegrityError(
                        "final-chance remote terminal does not bind its start"
                    )
                if event["status"] is None or event["evidence_identity"] is None or event["accounted_cny"] is None:
                    raise FinalChanceLedgerIntegrityError("final-chance remote terminal is incomplete")
                _require_sha256(str(event["evidence_identity"]), "evidence_identity")
                if _decimal(event["accounted_cny"], "accounted_cny") > _decimal(
                    event["worst_case_cny"], "worst_case_cny"
                ):
                    raise FinalChanceLedgerIntegrityError(
                        "final-chance remote terminal exceeds reserved cost"
                    )
                terminals.add(slot)
            else:
                raise FinalChanceLedgerIntegrityError("final-chance remote event type is unsupported")
            previous = declared
        self.snapshot()

    def snapshot(self) -> FinalChanceSnapshot:
        starts: dict[str, Mapping[str, object]] = {}
        terminals: dict[str, Mapping[str, object]] = {}
        for event in self.events:
            slot = str(event["slot_identity"])
            if event["event_type"] == NETWORK_ATTEMPT_STARTED:
                starts[slot] = event
            else:
                terminals[slot] = event
        total = self.historical_accounted_cny
        for slot, start in starts.items():
            terminal = terminals.get(slot)
            total += _decimal(
                start["worst_case_cny"] if terminal is None else terminal["accounted_cny"],
                "final-chance remote accounted cost",
            )
        if total > HARD_PROJECT_CAP_CNY:
            raise FinalChanceLedgerIntegrityError(
                "final-chance remote accounting exceeds the CNY100 hard cap"
            )
        return FinalChanceSnapshot(
            attempted_slots=frozenset(starts.keys()),
            project_accounted_cny=total,
            total_attempts=len(starts),
        )

    def append_start(
        self,
        *,
        now: datetime,
        provider_id: str,
        slot_identity: str,
        request_identity: str,
        worst_case_cny: Decimal,
    ) -> "FinalChanceRemoteExecutionLedger":
        if slot_identity in self.snapshot().attempted_slots:
            raise FinalChanceLedgerConflictError("final-chance remote slot has already been attempted")
        event = self._new_event(
            now=now,
            event_type=NETWORK_ATTEMPT_STARTED,
            provider_id=provider_id,
            slot_identity=slot_identity,
            request_identity=request_identity,
            worst_case_cny=worst_case_cny,
            start_event_identity=None,
            status=None,
            accounted_cny=None,
            evidence_identity=None,
        )
        return FinalChanceRemoteExecutionLedger(
            self.plan_identity, self.plan_sha256, (*self.events, event),
            historical_accounted_cny=self.historical_accounted_cny,
        )

    def append_terminal(
        self,
        *,
        now: datetime,
        provider_id: str,
        slot_identity: str,
        status: str,
        accounted_cny: Decimal,
        evidence_identity: str,
    ) -> "FinalChanceRemoteExecutionLedger":
        starts = [
            event for event in self.events
            if event["slot_identity"] == slot_identity and event["event_type"] == NETWORK_ATTEMPT_STARTED
        ]
        terminals = [
            event for event in self.events
            if event["slot_identity"] == slot_identity and event["event_type"] == ATTEMPT_TERMINAL
        ]
        if len(starts) != 1 or terminals:
            raise FinalChanceLedgerConflictError("final-chance remote slot cannot accept a terminal")
        start = starts[0]
        event = self._new_event(
            now=now,
            event_type=ATTEMPT_TERMINAL,
            provider_id=provider_id,
            slot_identity=slot_identity,
            request_identity=str(start["request_identity"]),
            worst_case_cny=_decimal(start["worst_case_cny"], "worst_case_cny"),
            start_event_identity=str(start["event_identity"]),
            status=status,
            accounted_cny=accounted_cny,
            evidence_identity=evidence_identity,
        )
        return FinalChanceRemoteExecutionLedger(
            self.plan_identity, self.plan_sha256, (*self.events, event),
            historical_accounted_cny=self.historical_accounted_cny,
        )


@dataclass(frozen=True)
class FinalChanceLedgerObservedState:
    head_sha: str | None
    ledger: FinalChanceRemoteExecutionLedger


class FinalChanceLedgerStore(Protocol):
    def load(self, plan_identity: str, plan_sha256: str) -> FinalChanceLedgerObservedState: ...

    def compare_and_swap(
        self,
        *,
        expected_head: str | None,
        ledger_bytes: bytes,
        evidence_artifacts: Mapping[str, bytes] | None = None,
    ) -> str: ...


class FinalChanceGitRemoteLedgerStore:
    """Git CAS store on the frozen final-chance remote ref (normal push = CAS)."""

    def __init__(
        self,
        *,
        repository: os.PathLike[str],
        remote: str = "origin",
        remote_ref: str = FINAL_CHANCE_REMOTE_REF,
    ) -> None:
        self.repository = os.fspath(repository)
        self.remote = remote
        self.remote_ref = remote_ref
        if remote_ref != FINAL_CHANCE_REMOTE_REF:
            raise FinalChanceLedgerVerificationError(
                "caller-selected final-chance remote ref is forbidden"
            )
        if not re.fullmatch(r"refs/heads/[A-Za-z0-9._/-]+", remote_ref):
            raise ValueError("remote_ref must be a full heads ref")
        if not re.fullmatch(r"[A-Za-z0-9._-]+", remote):
            raise ValueError("remote must be a configured Git remote name")

    def _run(self, args: Sequence[str], *, input_bytes: bytes | None = None) -> bytes:
        environment = dict(os.environ)
        for credential_name in _PROVIDER_CREDENTIAL_ENV_NAMES:
            environment.pop(credential_name, None)
        environment.setdefault("GIT_AUTHOR_NAME", "Final-Chance Live Lane")
        environment.setdefault("GIT_AUTHOR_EMAIL", "final-chance-live@invalid.local")
        environment.setdefault("GIT_COMMITTER_NAME", environment["GIT_AUTHOR_NAME"])
        environment.setdefault("GIT_COMMITTER_EMAIL", environment["GIT_AUTHOR_EMAIL"])
        try:
            completed = subprocess.run(
                ["git", *args],
                cwd=self.repository,
                input=input_bytes,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                env=environment,
            )
        except OSError as error:
            raise FinalChanceLedgerUnavailableError("Git remote state command is unavailable") from error
        if completed.returncode != 0:
            raise FinalChanceLedgerUnavailableError("Git remote state command failed")
        return completed.stdout

    def _remote_head(self) -> str | None:
        output = self._run(["ls-remote", "--heads", self.remote, self.remote_ref])
        if not output.strip():
            return None
        rows = output.decode("ascii", errors="strict").splitlines()
        if len(rows) != 1:
            raise FinalChanceLedgerVerificationError(
                "final-chance remote state ref did not resolve uniquely"
            )
        fields = rows[0].split()
        if len(fields) != 2 or fields[1] != self.remote_ref or _GIT_OID.fullmatch(fields[0]) is None:
            raise FinalChanceLedgerVerificationError(
                "final-chance remote state ref response is malformed"
            )
        return fields[0]

    def _read_file_at(self, commit_sha: str, filename: str) -> bytes:
        return self._run(["show", f"{commit_sha}:{filename}"])

    def _tree_entries_at(self, commit_sha: str) -> dict[str, str]:
        entries: dict[str, str] = {}
        for row in self._run(["ls-tree", commit_sha]).decode("utf-8").splitlines():
            try:
                metadata, filename = row.split("\t", 1)
            except ValueError as error:
                raise FinalChanceLedgerVerificationError("final-chance remote tree entry is malformed") from error
            parts = metadata.split()
            if (
                len(parts) != 3
                or parts[0] != "100644"
                or parts[1] != "blob"
                or _GIT_OID.fullmatch(parts[2]) is None
                or (
                    filename != FINAL_CHANCE_LEDGER_FILENAME
                    and re.fullmatch(r"evidence-[0-9a-f]{64}\.json", filename) is None
                )
                or filename in entries
            ):
                raise FinalChanceLedgerVerificationError(
                    "final-chance remote tree contains an unsupported or duplicate entry"
                )
            entries[filename] = parts[2]
        if FINAL_CHANCE_LEDGER_FILENAME not in entries:
            raise FinalChanceLedgerVerificationError("final-chance remote tree is missing its ledger")
        return entries

    def load(self, plan_identity: str, plan_sha256: str) -> FinalChanceLedgerObservedState:
        head = self._remote_head()
        if head is None:
            empty = FinalChanceRemoteExecutionLedger(plan_identity, plan_sha256)
            return FinalChanceLedgerObservedState(None, empty)
        fetch_ref = f"refs/final-chance-live/observed"
        self._run(["fetch", "--no-tags", self.remote, f"{self.remote_ref}:{fetch_ref}"])
        entries = self._tree_entries_at(head)
        raw = self._read_file_at(head, FINAL_CHANCE_LEDGER_FILENAME)
        ledger = FinalChanceRemoteExecutionLedger.from_bytes(plan_identity, plan_sha256, raw)
        terminals = [
            event for event in ledger.events if event["event_type"] == ATTEMPT_TERMINAL
        ]
        expected_evidence_names = {
            f'evidence-{event["evidence_identity"]}.json' for event in terminals
        }
        actual_evidence_names = set(entries) - {FINAL_CHANCE_LEDGER_FILENAME}
        if actual_evidence_names != expected_evidence_names:
            raise FinalChanceLedgerIntegrityError(
                "final-chance remote evidence file set differs from terminal identities"
            )
        return FinalChanceLedgerObservedState(head, ledger)

    def compare_and_swap(
        self,
        *,
        expected_head: str | None,
        ledger_bytes: bytes,
        evidence_artifacts: Mapping[str, bytes] | None = None,
        plan_identity: str | None = None,
        plan_sha256: str | None = None,
    ) -> str:
        del plan_identity, plan_sha256
        if self._remote_head() != expected_head:
            raise FinalChanceLedgerConflictError(
                "final-chance remote state head changed before reservation"
            )
        artifacts = dict(evidence_artifacts or {})
        files = {FINAL_CHANCE_LEDGER_FILENAME: ledger_bytes, **artifacts}
        retained_entries: dict[str, str] = {}
        if expected_head is not None:
            retained_entries.update(self._tree_entries_at(expected_head))
        for filename, content in sorted(files.items()):
            if filename != FINAL_CHANCE_LEDGER_FILENAME and re.fullmatch(
                r"evidence-[0-9a-f]{64}\.json", filename
            ) is None:
                raise FinalChanceLedgerVerificationError(
                    "final-chance remote evidence filename is invalid"
                )
            blob = self._run(["hash-object", "-w", "--stdin"], input_bytes=content).decode("ascii").strip()
            if _GIT_OID.fullmatch(blob) is None:
                raise FinalChanceLedgerVerificationError("Git returned an invalid blob identity")
            retained_entries[filename] = blob
        entries = [
            f"100644 blob {blob}\t{filename}\n"
            for filename, blob in sorted(retained_entries.items())
        ]
        tree = self._run(["mktree"], input_bytes="".join(entries).encode("utf-8")).decode("ascii").strip()
        commit_args = ["commit-tree", tree]
        if expected_head is not None:
            commit_args.extend(["-p", expected_head])
        commit_args.extend(["-m", "final-chance: persist V0.2 remote execution state"])
        commit = self._run(commit_args).decode("ascii").strip()
        try:
            self._run(["push", "--porcelain", self.remote, f"{commit}:{self.remote_ref}"])
        except FinalChanceLedgerUnavailableError as error:
            raise FinalChanceLedgerConflictError("final-chance remote state CAS push failed") from error
        if self._remote_head() != commit:
            raise FinalChanceLedgerVerificationError(
                "final-chance remote state head differs after CAS push"
            )
        self._run(["fetch", "--no-tags", self.remote, f"{self.remote_ref}:refs/final-chance-live/verified"])
        for filename, expected in files.items():
            if self._read_file_at(commit, filename) != expected:
                raise FinalChanceLedgerVerificationError(
                    "final-chance remote state bytes differ after persistence"
                )
        return commit


class FinalChanceInMemoryLedgerStore:
    """Test-only CAS store; not a production authority."""

    def __init__(self) -> None:
        self._head: str | None = None
        self._blob: bytes | None = None
        self._artifacts: dict[str, bytes] = {}

    def load(self, plan_identity: str, plan_sha256: str) -> FinalChanceLedgerObservedState:
        if self._blob is None:
            empty = FinalChanceRemoteExecutionLedger(plan_identity, plan_sha256)
            return FinalChanceLedgerObservedState(None, empty)
        ledger = FinalChanceRemoteExecutionLedger.from_bytes(plan_identity, plan_sha256, self._blob)
        return FinalChanceLedgerObservedState(self._head, ledger)

    def compare_and_swap(
        self,
        *,
        expected_head: str | None,
        ledger_bytes: bytes,
        evidence_artifacts: Mapping[str, bytes] | None = None,
    ) -> str:
        if self._head != expected_head:
            raise FinalChanceLedgerConflictError("in-memory head changed before reservation")
        new_head = _hash_bytes(ledger_bytes)
        self._head = new_head
        self._blob = ledger_bytes
        self._artifacts = dict(evidence_artifacts or {})
        return new_head

    def artifacts(self) -> Mapping[str, bytes]:
        return dict(self._artifacts)

    @property
    def head(self) -> str | None:
        return self._head


# ---------------------------------------------------------------------------
# 6. Evidence capture
# ---------------------------------------------------------------------------
def build_final_chance_success_evidence(
    *,
    plan: Mapping[str, object],
    sample: Mapping[str, object],
    slot_identity: str,
    provider_id: str,
    model_id: str,
    request: V03Request,
    prompt_hashes: dict[str, str],
    invocation: V03InvocationEvidence,
    normalized,
    request_started_at: datetime,
    response_at: datetime,
    http_status: int,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "artifact_schema_version": FINAL_CHANCE_SLOT_EVIDENCE_SCHEMA_VERSION,
        "pilot_id": PILOT_ID,
        "pilot_plan_identity": str(plan["pilot_plan_identity"]),
        "plan_file_sha256": committed_plan_file_sha256(),
        "slot_identity": slot_identity,
        "attempt_identity": request.attempt_identity.identity,
        "case_identity": prompt_hashes["case_identity"],
        "sample_id": str(sample["sample_id"]),
        "sample_identity": str(sample["sample_identity"]),
        "provider_id": provider_id,
        "model_id": model_id,
        "request_identity": request.identity,
        "prompt_identities": {
            "system_prompt_sha256": str(plan["system_prompt_sha256"]),
            "decision_prompt_sha256": str(plan["decision_prompt_sha256"]),
            "decision_prompt_addendum_sha256": str(plan["decision_prompt_addendum_sha256"]),
            "final_decision_prompt_sha256": prompt_hashes["final_decision_prompt_sha256"],
        },
        "input_identities": {
            "full_structured_observation_identity": str(sample["full_structured_observation_identity"]),
            "lower_input_contract_identity": str(sample["lower_input_contract_identity"]),
            "higher_timeframe_descriptor_identity": str(sample["higher_timeframe_descriptor_identity"]),
            "png_sha256": str(sample["png_sha256"]),
            "visual_artifact_identity": str(sample["visual_artifact_identity"]),
            "visual_input_identity": str(sample["visual_input_identity"]),
            "source_observation_identity": prompt_hashes["source_observation_identity"],
            "selected_context_identity": str(plan.get("jianghe_context_binding", {}).get("selected_context_identity")),
        },
        "request_started_at": _utc(request_started_at),
        "response_at": _utc(response_at),
        "elapsed_ms": max(0, int((response_at - request_started_at).total_seconds() * 1000)),
        "http_status": http_status,
        "provider_request_id": invocation.provider_request_id,
        "model_raw_final_answer": invocation.model_raw_final_answer,
        "final_content_sha256": invocation.final_content_sha256,
        "finish_reason": invocation.finish_reason,
        "normalized_evaluation_view": {
            "identity": normalized.identity,
            "family": normalized.family,
            "action": normalized.action,
            "direction": normalized.direction,
            "missing_headings": list(normalized.missing_headings),
            "invalid_enum_fields": list(normalized.invalid_enum_fields),
            "scoreable": normalized.scoreable,
        },
        "token_usage": None if invocation.usage is None else {
            "prompt_tokens": invocation.usage.prompt_tokens,
            "cached_input_tokens": invocation.usage.cached_input_tokens,
            "image_tokens": invocation.usage.image_tokens,
            "reasoning_tokens": invocation.usage.reasoning_tokens,
            "completion_tokens": invocation.usage.completion_tokens,
        },
        "cost_metadata": {
            "precall_conservative_reservation_cny": invocation.precall_conservative_reservation_cny,
            "postcall_calculated_cny": invocation.postcall_calculated_cny,
            "provider_reported_billed_cny": invocation.provider_reported_billed_cny,
            "accounted_cny_for_hard_cap": invocation.accounted_cny_for_hard_cap,
            "rate_card_identity": invocation.rate_card_identity,
        },
        "execution_status": "SUCCESS",
        "failure_classification": None,
        "automatic_retry": 0,
        "automatic_next_slot": 0,
        "outcome_future_access": "NO",
        "credential_value_exposed": False,
        "hidden_reasoning_persisted": False,
    }
    return payload


def build_final_chance_failure_evidence(
    *,
    plan: Mapping[str, object],
    sample: Mapping[str, object],
    slot_identity: str,
    provider_id: str,
    model_id: str,
    request: V03Request | None,
    prompt_hashes: dict[str, str] | None,
    failure_classification: str,
    error: BaseException | None,
    network_started: bool,
    reservation_cny: Decimal,
    request_started_at: datetime | None,
    response_at: datetime,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "artifact_schema_version": FINAL_CHANCE_SLOT_EVIDENCE_SCHEMA_VERSION,
        "pilot_id": PILOT_ID,
        "pilot_plan_identity": str(plan["pilot_plan_identity"]),
        "plan_file_sha256": committed_plan_file_sha256(),
        "slot_identity": slot_identity,
        "attempt_identity": None if request is None else request.attempt_identity.identity,
        "case_identity": None if prompt_hashes is None else prompt_hashes.get("case_identity"),
        "sample_id": str(sample["sample_id"]),
        "sample_identity": str(sample["sample_identity"]),
        "provider_id": provider_id,
        "model_id": model_id,
        "request_identity": None if request is None else request.identity,
        "prompt_identities": None if prompt_hashes is None else {
            "system_prompt_sha256": str(plan["system_prompt_sha256"]),
            "decision_prompt_sha256": str(plan["decision_prompt_sha256"]),
            "decision_prompt_addendum_sha256": str(plan["decision_prompt_addendum_sha256"]),
            "final_decision_prompt_sha256": prompt_hashes["final_decision_prompt_sha256"],
        },
        "input_identities": {
            "full_structured_observation_identity": str(sample["full_structured_observation_identity"]),
            "lower_input_contract_identity": str(sample["lower_input_contract_identity"]),
            "higher_timeframe_descriptor_identity": str(sample["higher_timeframe_descriptor_identity"]),
            "png_sha256": str(sample["png_sha256"]),
            "visual_artifact_identity": str(sample["visual_artifact_identity"]),
            "visual_input_identity": str(sample["visual_input_identity"]),
            "source_observation_identity": None if prompt_hashes is None else prompt_hashes.get("source_observation_identity"),
        },
        "request_started_at": None if request_started_at is None else _utc(request_started_at),
        "response_at": _utc(response_at),
        "elapsed_ms": (
            None
            if request_started_at is None
            else max(0, int((response_at - request_started_at).total_seconds() * 1000))
        ),
        "http_status": None,
        "provider_request_id": None,
        "model_raw_final_answer": None,
        "final_content_sha256": None,
        "finish_reason": None,
        "normalized_evaluation_view": None,
        "token_usage": None,
        "cost_metadata": {
            "precall_conservative_reservation_cny": _decimal_text(reservation_cny),
            "postcall_calculated_cny": _decimal_text(reservation_cny),
            "provider_reported_billed_cny": None,
            "accounted_cny_for_hard_cap": _decimal_text(reservation_cny),
        },
        "execution_status": "FAILED",
        "failure_classification": failure_classification,
        "error_type": type(error).__name__ if error is not None else None,
        "error_message": str(error) if error is not None else None,
        "network_started": network_started,
        "automatic_retry": 0,
        "automatic_next_slot": 0,
        "outcome_future_access": "NO",
        "credential_value_exposed": False,
        "hidden_reasoning_persisted": False,
    }
    return payload


def classify_final_chance_failure(error: BaseException) -> str:
    if isinstance(error, V03ModelMismatchError):
        return "PROVIDER_MODEL_MISMATCH"
    if isinstance(error, ValueError):
        return "PROVIDER_RESPONSE_MALFORMED"
    if isinstance(error, PaidCallNotAuthorizedError):
        return "PAID_CALL_NOT_AUTHORIZED"
    message = str(error)
    if "HTTP" in message:
        return "TRANSPORT_HTTP_ERROR"
    if "credential" in message.lower():
        return "MISSING_CREDENTIAL"
    return "INFRASTRUCTURE_FAILURE"


# ---------------------------------------------------------------------------
# 7. Preflight + single-slot execution
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FinalChancePreflightResult:
    provider_id: str
    sample_id: str
    slot_identity: str
    passed: bool
    gates: Mapping[str, str]
    worst_case_reservation_cny: str
    shared_accounted_cny: str
    remaining_cny: str


@dataclass(frozen=True)
class FinalChanceSlotResult:
    provider_id: str
    sample_id: str
    slot_identity: str
    status: str
    accounted_cny: Decimal
    evidence_identity: str
    remote_start_head: str | None
    remote_terminal_head: str | None
    dry_run: bool
    automatic_retries: int = 0
    automatic_next_slots: int = 0


def _verify_shared_ledger_authority() -> Decimal:
    """Cross-check the shared project ledger carry-forward against committed evidence."""
    try:
        blob = _repository_blob_bytes(PILOT_PILOT_SUMMARY_PATH)
        payload = json.loads(blob.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise FinalChanceLedgerError("shared ledger authority evidence is unreadable") from error
    if not isinstance(payload, Mapping):
        raise FinalChanceLedgerError("shared ledger authority evidence must be an object")
    recorded = payload.get("project_accounted_cny_after")
    if recorded is None:
        raise FinalChanceLedgerError("shared ledger authority lacks project_accounted_cny_after")
    if _decimal(recorded, "project_accounted_cny_after") != FINAL_CHANCE_HISTORICAL_PROJECT_ACCOUNTED_CNY:
        raise FinalChanceLedgerError(
            "shared ledger authority value drifted from the committed pilot summary"
        )
    return FINAL_CHANCE_HISTORICAL_PROJECT_ACCOUNTED_CNY


def preflight_final_chance_slot(
    *,
    plan: Mapping[str, object],
    provider_id: str,
    sample_id: str,
    now: datetime,
    slot_authority: FinalChanceExplicitSlotAuthority | None = None,
    store: FinalChanceLedgerStore | None = None,
    plan_file_sha256: str | None = None,
) -> FinalChancePreflightResult:
    """Run every fail-closed gate; raise on any failure and return a PASS report."""
    _require_aware(now, "now")
    if plan_file_sha256 is None:
        plan_file_sha256 = committed_plan_file_sha256()
    _require_sha256(plan_file_sha256, "plan_file_sha256")
    gates: dict[str, str] = {}

    request, transport, config, prompt_hashes = build_final_chance_request(
        plan, provider_id=provider_id, sample_id=sample_id, now=now
    )
    slot_identity = find_final_chance_slot_identity(plan, provider_id, sample_id)
    gates["A_PLAN_IDENTITY"] = "PASS"
    gates["B_CASE_EXISTS"] = "PASS"
    gates["C_PROVIDER_MODEL"] = "PASS"
    gates["D_PAYLOAD_IDENTITIES"] = "PASS"

    spec = provider_spec_for(provider_id)
    rate_card = load_current_repository_rate_card(spec, now=now)
    worst, image_bound = compute_final_chance_reservation(request, transport, config, rate_card)
    del image_bound

    if slot_authority is None:
        raise FinalChanceGateError("NEXT_EXPLICIT_PAID_SLOT=NONE; no explicit slot authority exists")
    if slot_authority.explicit_slot_identity != slot_identity:
        raise FinalChanceGateError(
            "slot authority does not match the requested slot identity"
        )
    if slot_authority.provider_id != provider_id or slot_authority.sample_id != sample_id:
        raise FinalChanceGateError("slot authority provider/sample differs from the requested slot")
    if slot_authority.model_id != config.model_id:
        raise FinalChanceGateError("slot authority model differs from the frozen slot model")
    if slot_authority.plan_identity != str(plan["pilot_plan_identity"]):
        raise FinalChanceGateError("slot authority plan binding differs from the materialized plan")
    if slot_authority.plan_file_sha256 != plan_file_sha256:
        raise FinalChanceGateError("slot authority plan-file binding differs")
    if slot_authority.case_identity != prompt_hashes["case_identity"]:
        raise FinalChanceGateError("slot authority case binding differs from the plan")
    if not (slot_authority.effective_at <= now < slot_authority.expires_at):
        raise FinalChanceGateError("explicit slot authority is stale or not yet effective")
    gates["E_EXPLICIT_SLOT_AUTHORITY"] = "PASS"

    paid_auth = load_owner_paid_call_authorization(now=now)
    if not paid_auth.permits(spec):
        raise FinalChanceGateError("current Owner paid-call authorization does not permit provider/model")
    if slot_authority.authorization_id != paid_auth.authorization_id:
        raise FinalChanceGateError("slot authority authorization binding differs from current authority")
    if slot_authority.rate_card_identity != rate_card.identity:
        raise FinalChanceGateError("slot authority rate-card binding differs from current pricing")
    gates["PAID_AUTHORIZATION"] = "PASS"
    gates["RATE_CARD"] = "PASS"

    _verify_shared_ledger_authority()

    if store is not None:
        observed = store.load(str(plan["pilot_plan_identity"]), plan_file_sha256)
        snapshot = observed.ledger.snapshot()
        if slot_identity in snapshot.attempted_slots:
            raise FinalChanceGateError("slot attempt already exists; re-execution is forbidden")
        shared_accounted = snapshot.project_accounted_cny
        gates["F_ATTEMPT_FRESH"] = "PASS"
        gates["SHARED_LEDGER"] = "PASS"
    else:
        shared_accounted = FINAL_CHANCE_HISTORICAL_PROJECT_ACCOUNTED_CNY
        gates["SHARED_LEDGER"] = "PASS"

    remaining = HARD_PROJECT_CAP_CNY - shared_accounted
    if shared_accounted + worst > HARD_PROJECT_CAP_CNY:
        raise FinalChanceGateError("worst-case reservation would exceed the CNY100 hard cap")
    gates["HARD_CAP"] = "PASS"
    gates["AUTOMATIC_RETRY"] = "FORBIDDEN"
    gates["AUTOMATIC_NEXT_SLOT"] = "FORBIDDEN"

    return FinalChancePreflightResult(
        provider_id=provider_id,
        sample_id=sample_id,
        slot_identity=slot_identity,
        passed=True,
        gates=gates,
        worst_case_reservation_cny=_decimal_text(worst) or "0",
        shared_accounted_cny=_decimal_text(shared_accounted) or "0",
        remaining_cny=_decimal_text(remaining) or "0",
    )


def execute_final_chance_slot(
    *,
    provider_id: str,
    sample_id: str,
    now: datetime,
    store: FinalChanceLedgerStore,
    slot_authority: FinalChanceExplicitSlotAuthority,
    http_post: Callable | None = None,
    credential_lookup: Callable[[str], str | None] | None = None,
    dry_run: bool = False,
    plan_bytes: bytes | None = None,
) -> FinalChanceSlotResult:
    """Execute exactly one frozen V0.2 slot behind a durable write-ahead lane."""
    _require_aware(now, "now")
    plan = load_verified_final_chance_plan(plan_bytes=plan_bytes)
    plan_file_sha = committed_plan_file_sha256(plan_bytes)
    preflight = preflight_final_chance_slot(
        plan=plan,
        provider_id=provider_id,
        sample_id=sample_id,
        now=now,
        slot_authority=slot_authority,
        store=store,
        plan_file_sha256=plan_file_sha,
    )
    if dry_run:
        return FinalChanceSlotResult(
            provider_id=provider_id,
            sample_id=sample_id,
            slot_identity=preflight.slot_identity,
            status="PREFLIGHT_PASS",
            accounted_cny=Decimal("0"),
            evidence_identity=None,
            remote_start_head=None,
            remote_terminal_head=None,
            dry_run=True,
        )

    sample = next(item for item in plan["samples"] if item.get("sample_id") == sample_id)
    request, transport, config, prompt_hashes = build_final_chance_request(
        plan, provider_id=provider_id, sample_id=sample_id, now=now
    )
    slot_identity = find_final_chance_slot_identity(plan, provider_id, sample_id)
    spec = provider_spec_for(provider_id)
    rate_card = load_current_repository_rate_card(spec, now=now)
    worst, image_bound = compute_final_chance_reservation(request, transport, config, rate_card)

    observed = store.load(str(plan["pilot_plan_identity"]), plan_file_sha)
    snapshot = observed.ledger.snapshot()
    if slot_identity in snapshot.attempted_slots:
        raise FinalChanceGateError("slot attempt already exists; re-execution is forbidden")

    ledger = observed.ledger
    ledger_start = ledger.append_start(
        now=now,
        provider_id=provider_id,
        slot_identity=slot_identity,
        request_identity=request.identity,
        worst_case_cny=worst,
    )
    start_head = store.compare_and_swap(
        expected_head=observed.head_sha,
        ledger_bytes=ledger_start.to_bytes(),
    )

    budget = V03BudgetLedger(historical_accounted_cny=snapshot.project_accounted_cny)
    request_started_at = now
    terminal_status = V03TerminalStatus.INFRASTRUCTURE_FAILURE.value
    accounted = worst
    evidence_payload: dict[str, object]
    response_at = now
    try:
        invocation = transport.invoke(
            request,
            budget=budget,
            rate_card=rate_card,
            max_image_tokens=image_bound,
            now=now,
            api_key=(None if credential_lookup is None else credential_lookup(config.api_key_env)),
            http_post=http_post,
        )
        response_at = datetime.now(timezone.utc)
        normalized = V03CapabilityAdapter().adapt(
            invocation.model_raw_final_answer or "", truncated=invocation.finish_reason == "length"
        )
        terminal_status = (
            V03TerminalStatus.CAPABILITY_SCOREABLE.value
            if normalized.scoreable
            else V03TerminalStatus.CAPABILITY_NOT_SCOREABLE.value
        )
        accounted = _decimal(invocation.accounted_cny_for_hard_cap, "accounted_cny")
        evidence_payload = build_final_chance_success_evidence(
            plan=plan,
            sample=sample,
            slot_identity=slot_identity,
            provider_id=provider_id,
            model_id=config.model_id,
            request=request,
            prompt_hashes=prompt_hashes,
            invocation=invocation,
            normalized=normalized,
            request_started_at=request_started_at,
            response_at=response_at,
            http_status=200,
        )
    except Exception as error:  # noqa: BLE001 - deliberate fail-closed single attempt
        response_at = datetime.now(timezone.utc)
        failure = classify_final_chance_failure(error)
        terminal_status = (
            V03TerminalStatus.TRANSPORT_HTTP_ERROR.value
            if failure == "TRANSPORT_HTTP_ERROR"
            else V03TerminalStatus.PROVIDER_RESPONSE_MALFORMED.value
            if failure == "PROVIDER_RESPONSE_MALFORMED"
            else V03TerminalStatus.PROVIDER_MODEL_MISMATCH.value
            if failure == "PROVIDER_MODEL_MISMATCH"
            else V03TerminalStatus.INFRASTRUCTURE_FAILURE.value
        )
        evidence_payload = build_final_chance_failure_evidence(
            plan=plan,
            sample=sample,
            slot_identity=slot_identity,
            provider_id=provider_id,
            model_id=config.model_id,
            request=request,
            prompt_hashes=prompt_hashes,
            failure_classification=failure,
            error=error,
            network_started=True,
            reservation_cny=worst,
            request_started_at=request_started_at,
            response_at=response_at,
        )
    evidence_payload["evidence_identity"] = _hash(evidence_payload)
    evidence_bytes = (_canonical_json(evidence_payload) + "\n").encode("utf-8")
    ledger_terminal = ledger_start.append_terminal(
        now=response_at,
        provider_id=provider_id,
        slot_identity=slot_identity,
        status=terminal_status,
        accounted_cny=accounted,
        evidence_identity=str(evidence_payload["evidence_identity"]),
    )
    terminal_head = store.compare_and_swap(
        expected_head=start_head,
        ledger_bytes=ledger_terminal.to_bytes(),
        evidence_artifacts={
            f'evidence-{evidence_payload["evidence_identity"]}.json': evidence_bytes
        },
    )
    return FinalChanceSlotResult(
        provider_id=provider_id,
        sample_id=sample_id,
        slot_identity=slot_identity,
        status=terminal_status,
        accounted_cny=accounted,
        evidence_identity=str(evidence_payload["evidence_identity"]),
        remote_start_head=start_head,
        remote_terminal_head=terminal_head,
        dry_run=False,
        automatic_retries=0,
        automatic_next_slots=0,
    )


__all__ = [
    "ATTEMPT_TERMINAL",
    "FINAL_CHANCE_HISTORICAL_PROJECT_ACCOUNTED_CNY",
    "FINAL_CHANCE_LEDGER_FILENAME",
    "FINAL_CHANCE_REMOTE_REF",
    "FINAL_CHANCE_SLOT_AUTHORITY_SCHEMA_VERSION",
    "FINAL_CHANCE_SLOT_EVIDENCE_SCHEMA_VERSION",
    "FinalChanceError",
    "FinalChanceExplicitSlotAuthority",
    "FinalChanceGateError",
    "FinalChanceGitRemoteLedgerStore",
    "FinalChanceInMemoryLedgerStore",
    "FinalChanceLedgerConflictError",
    "FinalChanceLedgerError",
    "FinalChanceLedgerIntegrityError",
    "FinalChanceLedgerObservedState",
    "FinalChanceLedgerStore",
    "FinalChanceLedgerUnavailableError",
    "FinalChanceLedgerVerificationError",
    "FinalChancePlanError",
    "FinalChancePreflightResult",
    "FinalChanceRemoteExecutionLedger",
    "FinalChanceSlotAuthorityError",
    "FinalChanceSlotResult",
    "FinalChanceSnapshot",
    "NEXT_EXPLICIT_PAID_SLOT_NONE",
    "NETWORK_ATTEMPT_STARTED",
    "PILOT_PLAN_IDENTITY",
    "PLAN_FILE_SHA256",
    "SLOT_AUTHORITY_PATH",
    "build_final_chance_request",
    "build_final_chance_failure_evidence",
    "build_final_chance_success_evidence",
    "classify_final_chance_failure",
    "committed_plan_file_sha256",
    "compute_final_chance_reservation",
    "execute_final_chance_slot",
    "final_decision_prompt",
    "find_final_chance_slot_identity",
    "image_input_bound",
    "load_final_chance_explicit_slot_authority",
    "load_final_chance_prompt_package",
    "load_verified_final_chance_plan",
    "preflight_final_chance_slot",
    "provider_spec_for",
    "reconstruct_final_chance_artifacts",
    "verify_final_chance_plan",
]

"""Owner-approved Stage-A Jianghe fidelity runtime.

This module isolates the five Stage-A qualification tracks without weakening the
generic pre-spend transport. It uses one deterministic synthetic observation
for JH-FIX-C-001, derives 15m/1H bars from the exact 5m bars, renders the
provider-neutral PNG with the integrated renderer, and keeps answer-bearing
fixture material out of VISUAL/STRUCTURED/DUAL requests.

No function here enables outcomes, broker access, provider tools, retries, or
automatic budget extension.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
import os
import time
from typing import Mapping, Sequence
from zoneinfo import ZoneInfo

from src.jianghe_ai_trader import JiangheObservation, ObservationBar, ObservationIdentity
from src.jianghe_prespend_runtime import (
    BudgetGuardError,
    CanonicalStructuredObservationArtifact,
    CnyBudgetLedger,
    DomesticProviderTransport,
    HARD_PROJECT_CAP_CNY,
    InvocationBounds,
    PaidCallAuthorization,
    PaidCallNotAuthorizedError,
    ProviderResponseError,
    ProviderTransportError,
    ProviderUsage,
    RateCard,
    SelectedJiangheContextArtifact,
    VisualInputArtifact,
    load_current_repository_rate_card,
    load_owner_paid_call_authorization,
)
from src.jianghe_response_normalizer import RESPONSE_SCHEMA_VERSION
from src.jianghe_source_only_verification import ROOT as REPOSITORY_ROOT, _repository_blob_bytes
from src.jianghe_visual_renderer import (
    JiangheVisualRenderer,
    RENDERER_VERSION,
    RendererConfig,
    VisualObservationSpec,
    VisualPanel,
)


STAGE_A_PROTOCOL_VERSION = "JIANGHE_STAGE_A_INPUT_PROTOCOL_V0_1"
STAGE_A_STIMULUS_VERSION = "JIANGHE_STAGE_A_SYNTHETIC_STIMULUS_V0_1"
STAGE_A_REQUEST_VERSION = "JIANGHE_STAGE_A_REQUEST_V0_1"
STAGE_A_EVIDENCE_VERSION = "JIANGHE_STAGE_A_PROVIDER_EVIDENCE_V0_1"
STAGE_A_PLAN_VERSION = "JIANGHE_STAGE_A_FROZEN_PLAN_V0_1"
QUALIFICATION_FIXTURE_ID = "JH-FIX-C-001"
STAGE_A_TOTAL_CAP_CNY = Decimal("18.00")
STAGE_A_PROVIDER_CAP_CNY = Decimal("6.00")
STAGE_A_MAX_CALLS_PER_PROVIDER = 5
SYNTHETIC_TIMEZONE = ZoneInfo("Asia/Shanghai")
SYNTHETIC_START = datetime(2026, 8, 1, 9, 0, tzinfo=SYNTHETIC_TIMEZONE)
SYNTHETIC_PRODUCT = "SYNTH"
SYNTHETIC_CONTRACT = "SYNTH.JH-C001"
FIDELITY_CORPUS_PATH = (
    REPOSITORY_ROOT / "docs" / "evidence" / "JIANGHE_AI_FIDELITY_FIXTURES_V0_1.json"
)


def _canonical_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _decimal_text(value: Decimal) -> str:
    if value == 0:
        return "0"
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


class StageAInputTrack(str, Enum):
    OPERATIONAL_PROVIDER = "OPERATIONAL_PROVIDER"
    SEMANTIC = "SEMANTIC"
    VISUAL = "VISUAL"
    STRUCTURED = "STRUCTURED"
    DUAL_INPUT = "DUAL_INPUT"


CONTENT_TRACKS = (
    StageAInputTrack.SEMANTIC,
    StageAInputTrack.VISUAL,
    StageAInputTrack.STRUCTURED,
    StageAInputTrack.DUAL_INPUT,
)
ALL_TRACKS = (
    StageAInputTrack.OPERATIONAL_PROVIDER,
    StageAInputTrack.SEMANTIC,
    StageAInputTrack.VISUAL,
    StageAInputTrack.STRUCTURED,
    StageAInputTrack.DUAL_INPUT,
)


def runtime_response_json_schema() -> dict[str, object]:
    nullable_text = {
        "anyOf": [
            {"type": "string", "minLength": 1},
            {"type": "null"},
        ]
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "action",
            "attention_mode",
            "decision_state",
            "declared_unknown",
            "direction",
            "family",
            "numeric_claims",
            "principle_references",
            "rationale",
            "schema_version",
            "source_references",
        ],
        "properties": {
            "schema_version": {"const": RESPONSE_SCHEMA_VERSION},
            "family": {"type": "string", "enum": ["A", "B", "C", "D", "NONE"]},
            "action": {
                "type": "string",
                "enum": ["WAIT", "NO_TRADE", "WATCH", "CANDIDATE", "ENTER", "MANAGE", "EXIT"],
            },
            "direction": {"type": "string", "enum": ["LONG", "SHORT", "NONE"]},
            "attention_mode": {
                "type": "string",
                "enum": ["SCAN", "WATCH", "CANDIDATE", "IN_POSITION", "COOLDOWN", "SUSPENDED"],
            },
            "decision_state": {"type": "string", "minLength": 1},
            "rationale": {"type": "string", "minLength": 1},
            "declared_unknown": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "principle_references": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "source_references": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "numeric_claims": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["claim", "value", "unit", "source_reference"],
                    "properties": {
                        "claim": {"type": "string", "minLength": 1},
                        "value": {"type": "string", "minLength": 1},
                        "unit": nullable_text,
                        "source_reference": nullable_text,
                    },
                },
            },
        },
    }


def _load_qualification_fixture() -> Mapping[str, object]:
    blob = _repository_blob_bytes(FIDELITY_CORPUS_PATH)
    payload = json.loads(blob.decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("fidelity corpus must be an object")
    fixtures = payload.get("fixtures")
    if not isinstance(fixtures, list):
        raise ValueError("fidelity corpus fixtures must be a list")
    matches = [
        fixture
        for fixture in fixtures
        if isinstance(fixture, Mapping) and fixture.get("fixture_id") == QUALIFICATION_FIXTURE_ID
    ]
    if len(matches) != 1:
        raise ValueError("qualification fixture must resolve exactly once")
    return matches[0]


def qualification_visible_information() -> Mapping[str, object]:
    fixture = _load_qualification_fixture()
    visible = fixture.get("visible_information")
    expected_fields = {"situation", "timeframes", "market_state", "synthetic_observations"}
    if not isinstance(visible, Mapping) or set(visible) != expected_fields:
        raise ValueError("qualification visible_information schema drifted")
    if visible.get("timeframes") != ["1H", "15m", "5m"]:
        raise ValueError("qualification fixture timeframe contract drifted")
    return visible


def semantic_fixture_text() -> str:
    # Intentionally omits fixture_id/title/expected/rubric/hidden_future_information.
    return _canonical_json({"visible_information": qualification_visible_information()})


def _fine_close(index: int) -> Decimal:
    pattern = (
        Decimal("99.4"), Decimal("100.0"), Decimal("100.7"), Decimal("101.3"),
        Decimal("101.55"), Decimal("101.0"), Decimal("100.3"), Decimal("99.5"),
        Decimal("98.9"), Decimal("99.3"), Decimal("100.1"), Decimal("100.8"),
    )
    if index < 76:
        return pattern[index % len(pattern)]
    approach = {
        76: Decimal("100.8"), 77: Decimal("101.2"), 78: Decimal("101.55"),
        79: Decimal("101.7"), 80: Decimal("101.1"), 81: Decimal("100.8"),
        82: Decimal("100.9"), 83: Decimal("100.6"), 84: Decimal("100.8"),
        85: Decimal("100.5"), 86: Decimal("100.9"), 87: Decimal("100.7"),
        88: Decimal("101.0"), 89: Decimal("100.6"), 90: Decimal("100.9"),
        91: Decimal("100.7"), 92: Decimal("100.5"), 93: Decimal("100.8"),
        94: Decimal("100.6"), 95: Decimal("100.7"),
    }
    return approach[index]


def _fine_bars() -> tuple[ObservationBar, ...]:
    bars: list[ObservationBar] = []
    previous_close = Decimal("99.2")
    for index in range(96):
        open_time = SYNTHETIC_START + timedelta(minutes=5 * index)
        close_time = open_time + timedelta(minutes=5)
        close = _fine_close(index)
        open_price = previous_close
        if index == 80:
            high = Decimal("103.0")
            low = Decimal("100.9")
        else:
            high = max(open_price, close) + Decimal("0.25")
            low = min(open_price, close) - Decimal("0.25")
        volume = Decimal(100 + (index % 7) * 10)
        bars.append(
            ObservationBar(
                timeframe="5m",
                open_time=open_time,
                close_time=close_time,
                available_at=close_time,
                open_price=_decimal_text(open_price),
                high_price=_decimal_text(high),
                low_price=_decimal_text(low),
                close_price=_decimal_text(close),
                volume=_decimal_text(volume),
                is_closed=True,
            )
        )
        previous_close = close
    return tuple(bars)


def _aggregate(
    bars: Sequence[ObservationBar], *, group_size: int, timeframe: str
) -> tuple[ObservationBar, ...]:
    if len(bars) % group_size:
        raise ValueError("fine-bar count must divide evenly for deterministic aggregation")
    output: list[ObservationBar] = []
    for start in range(0, len(bars), group_size):
        group = bars[start : start + group_size]
        highs = [Decimal(item.high_price) for item in group]
        lows = [Decimal(item.low_price) for item in group]
        volumes = [Decimal(item.volume) for item in group]
        output.append(
            ObservationBar(
                timeframe=timeframe,
                open_time=group[0].open_time,
                close_time=group[-1].close_time,
                available_at=group[-1].close_time,
                open_price=group[0].open_price,
                high_price=_decimal_text(max(highs)),
                low_price=_decimal_text(min(lows)),
                close_price=group[-1].close_price,
                volume=_decimal_text(sum(volumes, Decimal("0"))),
                is_closed=True,
            )
        )
    return tuple(output)


@dataclass(frozen=True)
class StageAStimulus:
    observation: JiangheObservation
    structured: CanonicalStructuredObservationArtifact
    visual: VisualInputArtifact
    png_sha256: str
    renderer_config_identity: str
    renderer_input_identity: str
    visual_artifact_identity: str
    recipe_identity: str
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if self.structured.source_observation_identity != self.observation.identity.identity:
            raise ValueError("structured stimulus must bind the canonical observation")
        if self.visual.source_observation_identity != self.observation.identity.identity:
            raise ValueError("visual stimulus must bind the canonical observation")
        if self.visual.content_sha256 != self.png_sha256:
            raise ValueError("visual PNG hash mismatch")
        object.__setattr__(
            self,
            "identity",
            _hash(
                {
                    "version": STAGE_A_STIMULUS_VERSION,
                    "fixture_id": QUALIFICATION_FIXTURE_ID,
                    "observation_identity": self.observation.identity.identity,
                    "structured_identity": self.structured.identity,
                    "visual_identity": self.visual.identity,
                    "png_sha256": self.png_sha256,
                    "renderer_config_identity": self.renderer_config_identity,
                    "renderer_input_identity": self.renderer_input_identity,
                    "visual_artifact_identity": self.visual_artifact_identity,
                    "recipe_identity": self.recipe_identity,
                }
            ),
        )


def build_stage_a_stimulus() -> StageAStimulus:
    visible = qualification_visible_information()
    fine = _fine_bars()
    bars_15m = _aggregate(fine, group_size=3, timeframe="15m")
    bars_1h = _aggregate(fine, group_size=12, timeframe="1H")
    all_bars = fine + bars_15m + bars_1h
    as_of = fine[-1].close_time
    observation = JiangheObservation(
        identity=ObservationIdentity(
            decision_time=as_of,
            exchange_time=as_of,
            product=SYNTHETIC_PRODUCT,
            concrete_contract=SYNTHETIC_CONTRACT,
            mapping_identity=_hash(
                {
                    "version": STAGE_A_STIMULUS_VERSION,
                    "fixture_visible_information_sha256": sha256(
                        _canonical_json(visible).encode("utf-8")
                    ).hexdigest(),
                    "aggregation": {"5m_to_15m": 3, "5m_to_1H": 12},
                }
            ),
            session_identity=_hash(
                {
                    "synthetic_session": "DAY",
                    "timezone": "Asia/Shanghai",
                    "start": SYNTHETIC_START.isoformat(),
                }
            ),
        ),
        bars=all_bars,
        visible_metadata=(("session", "DAY"),),
    )
    structured = CanonicalStructuredObservationArtifact.from_observation(observation)
    rendered = JiangheVisualRenderer(RendererConfig()).render(
        VisualObservationSpec(
            product=SYNTHETIC_PRODUCT,
            concrete_contract=SYNTHETIC_CONTRACT,
            as_of=as_of,
            panels=(
                VisualPanel("1H", bars_1h),
                VisualPanel("15m", bars_15m),
                VisualPanel("5m", fine),
            ),
        )
    )
    visual = VisualInputArtifact(
        source_observation_identity=observation.identity.identity,
        renderer_identity=RENDERER_VERSION,
        png_bytes=rendered.png_bytes,
    )
    recipe_identity = _hash(
        {
            "version": STAGE_A_STIMULUS_VERSION,
            "fine_bars": [
                {
                    "open_time": item.open_time.isoformat(),
                    "close_time": item.close_time.isoformat(),
                    "open": item.open_price,
                    "high": item.high_price,
                    "low": item.low_price,
                    "close": item.close_price,
                    "volume": item.volume,
                }
                for item in fine
            ],
            "aggregation": {"15m_group": 3, "1H_group": 12},
            "visible_information_sha256": sha256(
                _canonical_json(visible).encode("utf-8")
            ).hexdigest(),
        }
    )
    return StageAStimulus(
        observation=observation,
        structured=structured,
        visual=visual,
        png_sha256=rendered.png_sha256,
        renderer_config_identity=rendered.renderer_config_identity,
        renderer_input_identity=rendered.input_observation_identity,
        visual_artifact_identity=rendered.visual_artifact_identity,
        recipe_identity=recipe_identity,
    )


@dataclass(frozen=True)
class StageAInputRequest:
    input_track: StageAInputTrack
    system_prompt: str
    decision_prompt: str
    response_schema: Mapping[str, object]
    context: SelectedJiangheContextArtifact
    stimulus: StageAStimulus
    max_output_tokens: int
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.input_track, StageAInputTrack):
            raise TypeError("input_track must be StageAInputTrack")
        if not self.system_prompt or not self.decision_prompt:
            raise ValueError("Stage-A prompts cannot be empty")
        if self.context.fixture_id != QUALIFICATION_FIXTURE_ID:
            raise ValueError("Stage-A context must be selected for the frozen qualification fixture")
        if not isinstance(self.max_output_tokens, int) or isinstance(self.max_output_tokens, bool):
            raise ValueError("max_output_tokens must be an integer")
        if not 1 <= self.max_output_tokens <= 2000:
            raise ValueError("Stage-A output cap must be in 1..2000")
        if dict(self.response_schema) != runtime_response_json_schema():
            raise ValueError("Stage-A response schema must equal the frozen runtime JSON Schema")
        object.__setattr__(
            self,
            "identity",
            _hash(
                {
                    "version": STAGE_A_REQUEST_VERSION,
                    "track": self.input_track.value,
                    "system_prompt_sha256": sha256(self.system_prompt.encode("utf-8")).hexdigest(),
                    "decision_prompt_sha256": sha256(self.decision_prompt.encode("utf-8")).hexdigest(),
                    "response_schema": self.response_schema,
                    "context_identity": self.context.identity,
                    "stimulus_identity": self.stimulus.identity,
                    "transmitted_structured_identity": self.transmitted_structured_identity,
                    "transmitted_visual_identities": tuple(item.identity for item in self.visuals),
                    "semantic_visible_information_sha256": (
                        sha256(semantic_fixture_text().encode("utf-8")).hexdigest()
                        if self.input_track is StageAInputTrack.SEMANTIC
                        else None
                    ),
                    "max_output_tokens": self.max_output_tokens,
                }
            ),
        )

    @property
    def structured_observation(self) -> CanonicalStructuredObservationArtifact:
        # Local provenance always exists even when this modality is not transmitted.
        return self.stimulus.structured

    @property
    def visuals(self) -> tuple[VisualInputArtifact, ...]:
        if self.input_track in {
            StageAInputTrack.VISUAL,
            StageAInputTrack.DUAL_INPUT,
            StageAInputTrack.OPERATIONAL_PROVIDER,
        }:
            return (self.stimulus.visual,)
        return ()

    @property
    def transmitted_structured_identity(self) -> str | None:
        if self.input_track in {
            StageAInputTrack.STRUCTURED,
            StageAInputTrack.DUAL_INPUT,
            StageAInputTrack.OPERATIONAL_PROVIDER,
        }:
            return self.stimulus.structured.identity
        return None

    def common_model_text(self) -> str:
        payload: dict[str, object] = {
            "jianghe_context": self.context.model_payload(),
            "decision_instruction": self.decision_prompt,
            "stage_a_input_track": self.input_track.value,
        }
        if self.input_track is StageAInputTrack.SEMANTIC:
            payload["visible_information"] = qualification_visible_information()
        elif self.input_track in {
            StageAInputTrack.STRUCTURED,
            StageAInputTrack.DUAL_INPUT,
            StageAInputTrack.OPERATIONAL_PROVIDER,
        }:
            payload["canonical_observation"] = self.stimulus.structured.payload()
        # VISUAL deliberately receives neither fixture prose nor structured observation.
        return _canonical_json(payload)


@dataclass
class StageABudgetEnvelope:
    total_cap_cny: Decimal = STAGE_A_TOTAL_CAP_CNY
    provider_cap_cny: Decimal = STAGE_A_PROVIDER_CAP_CNY
    spent_cny: Decimal = Decimal("0")
    provider_spent_cny: dict[str, Decimal] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.total_cap_cny = Decimal(self.total_cap_cny)
        self.provider_cap_cny = Decimal(self.provider_cap_cny)
        self.spent_cny = Decimal(self.spent_cny)
        if self.total_cap_cny != STAGE_A_TOTAL_CAP_CNY:
            raise ValueError("Stage-A total cap is frozen at CNY18")
        if self.provider_cap_cny != STAGE_A_PROVIDER_CAP_CNY:
            raise ValueError("Stage-A provider cap is frozen at CNY6")
        if self.spent_cny < 0 or self.spent_cny > self.total_cap_cny:
            raise ValueError("Stage-A spent amount is invalid")
        normalized: dict[str, Decimal] = {}
        for provider, value in self.provider_spent_cny.items():
            amount = Decimal(value)
            if amount < 0 or amount > self.provider_cap_cny:
                raise ValueError("Stage-A provider spent amount is invalid")
            normalized[provider] = amount
        if sum(normalized.values(), Decimal("0")) != self.spent_cny:
            raise ValueError("Stage-A provider ledger must sum to total spent")
        self.provider_spent_cny = normalized

    def preflight(self, provider_id: str, worst_case_cny: Decimal) -> None:
        amount = Decimal(worst_case_cny)
        if amount <= 0:
            raise BudgetGuardError("Stage-A reservation must be positive")
        if self.spent_cny + amount > self.total_cap_cny:
            raise BudgetGuardError("Stage-A CNY18 envelope would be exceeded")
        provider_spent = self.provider_spent_cny.get(provider_id, Decimal("0"))
        if provider_spent + amount > self.provider_cap_cny:
            raise BudgetGuardError("Stage-A per-provider CNY6 envelope would be exceeded")

    def record(self, provider_id: str, consumed_cny: Decimal) -> None:
        amount = Decimal(consumed_cny)
        if amount < 0:
            raise ValueError("consumed_cny cannot be negative")
        if amount == 0:
            return
        self.preflight(provider_id, amount)
        self.spent_cny += amount
        self.provider_spent_cny[provider_id] = (
            self.provider_spent_cny.get(provider_id, Decimal("0")) + amount
        )


@dataclass(frozen=True)
class StageAProviderInvocationEvidence:
    input_track: StageAInputTrack
    request_identity: str
    source_observation_identity: str
    selected_context_identity: str
    context_selection_policy_identity: str
    local_structured_observation_identity: str
    transmitted_structured_observation_identity: str | None
    transmitted_visual_identities: tuple[str, ...]
    provider_spec_identity: str
    requested_model_id: str
    resolved_model_id: str
    provider_request_id: str
    raw_provider_response_body: str
    raw_response_text: str
    usage: ProviderUsage
    latency_ms: int
    rate_card_identity: str
    budget_reservation_id: str
    charged_cny: str
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.input_track, StageAInputTrack):
            raise TypeError("input_track must be StageAInputTrack")
        if not self.request_identity or not self.raw_response_text:
            raise ValueError("Stage-A invocation evidence is incomplete")
        object.__setattr__(
            self,
            "identity",
            _hash(
                {
                    "version": STAGE_A_EVIDENCE_VERSION,
                    "input_track": self.input_track.value,
                    "request_identity": self.request_identity,
                    "source_observation_identity": self.source_observation_identity,
                    "selected_context_identity": self.selected_context_identity,
                    "context_selection_policy_identity": self.context_selection_policy_identity,
                    "local_structured_observation_identity": self.local_structured_observation_identity,
                    "transmitted_structured_observation_identity": self.transmitted_structured_observation_identity,
                    "transmitted_visual_identities": self.transmitted_visual_identities,
                    "provider_spec_identity": self.provider_spec_identity,
                    "requested_model_id": self.requested_model_id,
                    "resolved_model_id": self.resolved_model_id,
                    "provider_request_id": self.provider_request_id,
                    "raw_provider_response_sha256": sha256(
                        self.raw_provider_response_body.encode("utf-8")
                    ).hexdigest(),
                    "raw_response_text_sha256": sha256(
                        self.raw_response_text.encode("utf-8")
                    ).hexdigest(),
                    "usage": {
                        "text_input_tokens": self.usage.text_input_tokens,
                        "image_tokens": self.usage.image_tokens,
                        "output_tokens": self.usage.output_tokens,
                    },
                    "latency_ms": self.latency_ms,
                    "rate_card_identity": self.rate_card_identity,
                    "budget_reservation_id": self.budget_reservation_id,
                    "charged_cny": self.charged_cny,
                }
            ),
        )


class StageAProviderTransport(DomesticProviderTransport):
    """Dedicated Stage-A invoke path with modality-specific evidence."""

    @staticmethod
    def _worst_case_cny(rate_card: RateCard, bounds: InvocationBounds) -> Decimal:
        return (
            Decimal(bounds.total_input_tokens) * rate_card.input_per_million
            + Decimal(bounds.max_output_tokens) * rate_card.output_per_million
        ) / Decimal(1_000_000)

    def invoke_stage_a(
        self,
        request: StageAInputRequest,
        *,
        authorization: PaidCallAuthorization | None,
        budget: CnyBudgetLedger,
        stage_budget: StageABudgetEnvelope,
        bounds: InvocationBounds,
        now: datetime,
        timeout_seconds: float = 60.0,
    ) -> StageAProviderInvocationEvidence:
        if not isinstance(request, StageAInputRequest):
            raise TypeError("request must be StageAInputRequest")
        if authorization is None:
            raise PaidCallNotAuthorizedError("paid provider call lacks explicit Owner authorization")
        repository_authorization = load_owner_paid_call_authorization(now=now)
        if authorization.identity != repository_authorization.identity:
            raise PaidCallNotAuthorizedError("caller authorization differs from committed Owner authority")
        if not authorization.permits(self.spec):
            raise PaidCallNotAuthorizedError("provider/model is outside committed Owner authorization")
        if authorization.hard_cap_cny != budget.cap_cny or budget.cap_cny != HARD_PROJECT_CAP_CNY:
            raise PaidCallNotAuthorizedError("authorization and shared project ledger cap must equal CNY100")
        if bounds.max_output_tokens != request.max_output_tokens:
            raise BudgetGuardError("request output cap must equal reserved output cap")

        rate_card = load_current_repository_rate_card(self.spec, now=now)
        if rate_card.currency != "CNY":
            raise BudgetGuardError("Stage-A supports only repository-bound CNY rate cards")
        payload_bytes = self.payload_bytes(request)
        required_text_bound = len(payload_bytes) * 2 + 8192
        if bounds.max_text_input_tokens != required_text_bound:
            raise BudgetGuardError(
                "text-input reservation must exactly match the canonical payload bound policy"
            )
        if rate_card.image_billing_mode == "FIXED_INPUT_TOKENS_PER_IMAGE":
            expected_image_tokens = (
                len(request.visuals) * int(rate_card.fixed_input_tokens_per_image or 0)
            )
        elif rate_card.image_billing_mode == "INPUT_TOKENS":
            expected_image_tokens = 0
        else:
            raise BudgetGuardError("unknown image billing mode fails closed before network")
        if bounds.max_image_tokens != expected_image_tokens:
            raise BudgetGuardError(
                "image-token reservation must exactly match the repository billing authority"
            )

        worst_case = self._worst_case_cny(rate_card, bounds)
        stage_budget.preflight(self.spec.provider_id, worst_case)
        project_before = budget.spent_cny

        reservation = budget.reserve(self.spec, rate_card, bounds, fx=None, now=now)
        api_key = os.environ.get(self.spec.api_key_env)
        if not api_key:
            budget.cancel_before_network(reservation.reservation_id, reason="MISSING_CREDENTIAL")
            raise ProviderTransportError("provider credential is unavailable")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        started = time.monotonic()
        raw_provider_response_body = ""
        raw_text = ""
        usage: ProviderUsage | None = None
        resolved_model = ""
        provider_request_id = ""
        latency_ms = 0
        try:
            try:
                response = self._http_post(
                    self.spec.endpoint, headers, payload_bytes, float(timeout_seconds)
                )
            except Exception:
                budget.consume_full_reservation_on_unknown_usage(reservation.reservation_id)
                raise
            latency_ms = max(0, int((time.monotonic() - started) * 1000))
            if response.status_code < 200 or response.status_code >= 300:
                budget.consume_full_reservation_on_unknown_usage(reservation.reservation_id)
                raise ProviderTransportError(f"provider returned HTTP {response.status_code}")
            try:
                raw_provider_response_body = response.body.decode("utf-8")
                decoded = json.loads(raw_provider_response_body)
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                budget.consume_full_reservation_on_unknown_usage(reservation.reservation_id)
                raise ProviderResponseError("provider returned malformed JSON") from error
            if not isinstance(decoded, Mapping):
                budget.consume_full_reservation_on_unknown_usage(reservation.reservation_id)
                raise ProviderResponseError("provider response top level must be an object")
            try:
                raw_text = self._extract_text(decoded)
                usage = self._extract_usage(decoded)
                resolved_model_raw = decoded.get("model")
                provider_request_id_raw = decoded.get("id")
                if not isinstance(resolved_model_raw, str) or not resolved_model_raw:
                    raise ProviderResponseError("provider-resolved model identity is missing")
                if not isinstance(provider_request_id_raw, str) or not provider_request_id_raw:
                    raise ProviderResponseError("provider request id is missing")
                resolved_model = resolved_model_raw
                provider_request_id = provider_request_id_raw
            except ProviderResponseError:
                budget.consume_full_reservation_on_unknown_usage(reservation.reservation_id)
                raise
            conservative_image_tokens = max(usage.image_tokens, expected_image_tokens)
            budget.reconcile(
                reservation.reservation_id,
                text_input_tokens=usage.text_input_tokens,
                image_tokens=conservative_image_tokens,
                output_tokens=usage.output_tokens,
                rate_card=rate_card,
                fx=None,
                now=now,
            )
        finally:
            consumed = budget.spent_cny - project_before
            if consumed > 0:
                stage_budget.record(self.spec.provider_id, consumed)

        if usage is None:
            raise AssertionError("successful Stage-A invocation must have usage")
        charged = budget.spent_cny - project_before
        return StageAProviderInvocationEvidence(
            input_track=request.input_track,
            request_identity=request.identity,
            source_observation_identity=request.stimulus.observation.identity.identity,
            selected_context_identity=request.context.identity,
            context_selection_policy_identity=request.context.context_selection_policy_identity,
            local_structured_observation_identity=request.stimulus.structured.identity,
            transmitted_structured_observation_identity=request.transmitted_structured_identity,
            transmitted_visual_identities=tuple(item.identity for item in request.visuals),
            provider_spec_identity=self.spec.identity,
            requested_model_id=self.spec.model_id,
            resolved_model_id=resolved_model,
            provider_request_id=provider_request_id,
            raw_provider_response_body=raw_provider_response_body,
            raw_response_text=raw_text,
            usage=usage,
            latency_ms=latency_ms,
            rate_card_identity=rate_card.identity,
            budget_reservation_id=reservation.reservation_id,
            charged_cny=_decimal_text(charged),
        )


def exact_invocation_bounds(
    transport: DomesticProviderTransport,
    request: StageAInputRequest,
    *,
    rate_card: RateCard,
) -> InvocationBounds:
    text_bound = transport.conservative_text_input_token_bound(request)
    if rate_card.image_billing_mode == "FIXED_INPUT_TOKENS_PER_IMAGE":
        image_bound = len(request.visuals) * int(rate_card.fixed_input_tokens_per_image or 0)
    elif rate_card.image_billing_mode == "INPUT_TOKENS":
        image_bound = 0
    else:
        raise BudgetGuardError("unknown image billing mode")
    return InvocationBounds(
        max_text_input_tokens=text_bound,
        max_image_tokens=image_bound,
        max_output_tokens=request.max_output_tokens,
    )


def make_stage_a_request(
    track: StageAInputTrack,
    *,
    system_prompt: str,
    decision_prompt: str,
    max_output_tokens: int = 800,
    stimulus: StageAStimulus | None = None,
) -> StageAInputRequest:
    if not isinstance(track, StageAInputTrack):
        raise TypeError("track must be StageAInputTrack")
    resolved_stimulus = stimulus if stimulus is not None else build_stage_a_stimulus()
    context = SelectedJiangheContextArtifact.from_fixture_id(QUALIFICATION_FIXTURE_ID)
    return StageAInputRequest(
        input_track=track,
        system_prompt=system_prompt,
        decision_prompt=decision_prompt,
        response_schema=runtime_response_json_schema(),
        context=context,
        stimulus=resolved_stimulus,
        max_output_tokens=max_output_tokens,
    )


__all__ = [
    "ALL_TRACKS",
    "CONTENT_TRACKS",
    "QUALIFICATION_FIXTURE_ID",
    "STAGE_A_MAX_CALLS_PER_PROVIDER",
    "STAGE_A_PLAN_VERSION",
    "STAGE_A_PROTOCOL_VERSION",
    "STAGE_A_PROVIDER_CAP_CNY",
    "STAGE_A_STIMULUS_VERSION",
    "STAGE_A_TOTAL_CAP_CNY",
    "StageABudgetEnvelope",
    "StageAInputRequest",
    "StageAInputTrack",
    "StageAProviderInvocationEvidence",
    "StageAProviderTransport",
    "StageAStimulus",
    "build_stage_a_stimulus",
    "exact_invocation_bounds",
    "make_stage_a_request",
    "qualification_visible_information",
    "runtime_response_json_schema",
    "semantic_fixture_text",
]

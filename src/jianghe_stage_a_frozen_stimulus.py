"""Frozen Stage-A synthetic stimulus and compact visual presentation.

The Owner-approved protocol leaves the exact numeric bar recipe/window as an
implementation detail until the first paid call. This module freezes a 36 x 5m
window (plus exact 15m/1H aggregations) selected only from the already generated
non-outcome JH-FIX-C-001 visible-information stimulus. It contains 20 pre-poke
5m bars expressing the prior range, the upper-boundary wick/poke, the close back
inside, and 15 subsequent 5m bars with no follow-through, while avoiding
unnecessary repeated JSON cost.

The visual uses the integrated deterministic renderer at 768x576. All providers
receive the same observation/PNG/structured bytes for the applicable tracks.
No outcome, provider response, credential, historical candidate data, or future
information is consulted.
"""

from __future__ import annotations

from decimal import Decimal
from hashlib import sha256
import json

from src.jianghe_ai_trader import JiangheObservation, ObservationIdentity
from src.jianghe_prespend_runtime import (
    CanonicalStructuredObservationArtifact,
    VisualInputArtifact,
)
from src.jianghe_stage_a_runtime import (
    STAGE_A_STIMULUS_VERSION,
    StageAStimulus,
    _aggregate,
    build_stage_a_stimulus,
)
from src.jianghe_visual_renderer import (
    JiangheVisualRenderer,
    RendererConfig,
    VisualObservationSpec,
    VisualPanel,
)


FROZEN_STAGE_A_FINE_BAR_COUNT = 36
FROZEN_STAGE_A_15M_BAR_COUNT = 12
FROZEN_STAGE_A_1H_BAR_COUNT = 3
FROZEN_STAGE_A_CANVAS_WIDTH = 768
FROZEN_STAGE_A_CANVAS_HEIGHT = 576
FROZEN_STAGE_A_CANDLE_BODY_WIDTH = 4
FROZEN_STAGE_A_CANDLE_GAP = 2
FROZEN_STAGE_A_PRICE_LABEL_GUTTER = 72
FROZEN_STAGE_A_WINDOW_VERSION = "JIANGHE_STAGE_A_VISIBLE_WINDOW_36X5M_V0_1"


def _canonical_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def frozen_stage_a_renderer_config() -> RendererConfig:
    return RendererConfig(
        canvas_width=FROZEN_STAGE_A_CANVAS_WIDTH,
        canvas_height=FROZEN_STAGE_A_CANVAS_HEIGHT,
        candle_body_width=FROZEN_STAGE_A_CANDLE_BODY_WIDTH,
        candle_gap=FROZEN_STAGE_A_CANDLE_GAP,
        price_label_gutter=FROZEN_STAGE_A_PRICE_LABEL_GUTTER,
    )


def build_frozen_stage_a_stimulus() -> StageAStimulus:
    """Freeze the last 36 visible 5m bars and exact derived 15m/1H bars."""
    base = build_stage_a_stimulus()
    base_fine = tuple(
        sorted(
            (bar for bar in base.observation.bars if bar.timeframe == "5m"),
            key=lambda bar: bar.open_time,
        )
    )
    if len(base_fine) != 96:
        raise ValueError("pre-freeze Stage-A fine-bar recipe drifted")
    fine = base_fine[-FROZEN_STAGE_A_FINE_BAR_COUNT:]
    bars_15m = _aggregate(fine, group_size=3, timeframe="15m")
    bars_1h = _aggregate(fine, group_size=12, timeframe="1H")
    if (len(fine), len(bars_15m), len(bars_1h)) != (
        FROZEN_STAGE_A_FINE_BAR_COUNT,
        FROZEN_STAGE_A_15M_BAR_COUNT,
        FROZEN_STAGE_A_1H_BAR_COUNT,
    ):
        raise ValueError("frozen Stage-A aggregation counts drifted")

    # The frozen 36-bar window is base fine indices 60..95. The sole deliberate
    # upper-boundary wick/poke remains original index 80 -> frozen index 20.
    poke = fine[20]
    if poke.high_price != "103" or poke.close_price != "101.1":
        raise ValueError("frozen Stage-A wick/poke anchor drifted")
    if any(Decimal(bar.high_price) >= Decimal("102") for bar in fine[:20] + fine[21:]):
        raise ValueError("frozen Stage-A window contains an unintended second upper-boundary poke")

    as_of = fine[-1].close_time
    mapping_identity = _hash(
        {
            "window_version": FROZEN_STAGE_A_WINDOW_VERSION,
            "source_pre_freeze_mapping_identity": base.observation.identity.mapping_identity,
            "fine_window_first_open": fine[0].open_time.isoformat(),
            "fine_window_last_close": fine[-1].close_time.isoformat(),
            "fine_bar_count": len(fine),
            "aggregation": {"5m_to_15m": 3, "5m_to_1H": 12},
        }
    )
    observation = JiangheObservation(
        identity=ObservationIdentity(
            decision_time=as_of,
            exchange_time=as_of,
            product=base.observation.identity.product,
            concrete_contract=base.observation.identity.concrete_contract,
            mapping_identity=mapping_identity,
            session_identity=base.observation.identity.session_identity,
        ),
        bars=fine + bars_15m + bars_1h,
        visible_metadata=base.observation.visible_metadata,
    )
    structured = CanonicalStructuredObservationArtifact.from_observation(observation)

    rendered = JiangheVisualRenderer(frozen_stage_a_renderer_config()).render(
        VisualObservationSpec(
            product=observation.identity.product,
            concrete_contract=observation.identity.concrete_contract,
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
        renderer_identity=rendered.renderer_config_identity,
        png_bytes=rendered.png_bytes,
    )
    recipe_identity = _hash(
        {
            "version": STAGE_A_STIMULUS_VERSION,
            "window_version": FROZEN_STAGE_A_WINDOW_VERSION,
            "fine_bars": [
                {
                    "open_time": bar.open_time.isoformat(),
                    "close_time": bar.close_time.isoformat(),
                    "open": bar.open_price,
                    "high": bar.high_price,
                    "low": bar.low_price,
                    "close": bar.close_price,
                    "volume": bar.volume,
                }
                for bar in fine
            ],
            "aggregation": {"15m_group": 3, "1H_group": 12},
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


__all__ = [
    "FROZEN_STAGE_A_15M_BAR_COUNT",
    "FROZEN_STAGE_A_1H_BAR_COUNT",
    "FROZEN_STAGE_A_CANVAS_HEIGHT",
    "FROZEN_STAGE_A_CANVAS_WIDTH",
    "FROZEN_STAGE_A_CANDLE_BODY_WIDTH",
    "FROZEN_STAGE_A_CANDLE_GAP",
    "FROZEN_STAGE_A_FINE_BAR_COUNT",
    "FROZEN_STAGE_A_PRICE_LABEL_GUTTER",
    "FROZEN_STAGE_A_WINDOW_VERSION",
    "build_frozen_stage_a_stimulus",
    "frozen_stage_a_renderer_config",
]

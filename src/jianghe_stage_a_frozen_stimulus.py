"""Frozen Stage-A visual stimulus presentation.

This module keeps the already-approved synthetic market observation and bar recipe
unchanged, but freezes a compact provider-neutral renderer configuration before
the first paid call. The compact canvas remains fully deterministic, keeps all
96 x 5m / 32 x 15m / 8 x 1H bars visible, and stays below the DeepSeek launch
image-pixel budget so provider-side downscaling is less likely to erase wick detail.

No outcome, provider response, credential, or future information is consulted.
"""

from __future__ import annotations

from src.jianghe_prespend_runtime import VisualInputArtifact
from src.jianghe_stage_a_runtime import StageAStimulus, build_stage_a_stimulus
from src.jianghe_visual_renderer import (
    JiangheVisualRenderer,
    RendererConfig,
    VisualObservationSpec,
    VisualPanel,
)


FROZEN_STAGE_A_CANVAS_WIDTH = 768
FROZEN_STAGE_A_CANVAS_HEIGHT = 576
FROZEN_STAGE_A_CANDLE_BODY_WIDTH = 4
FROZEN_STAGE_A_CANDLE_GAP = 2
FROZEN_STAGE_A_PRICE_LABEL_GUTTER = 72


def frozen_stage_a_renderer_config() -> RendererConfig:
    return RendererConfig(
        canvas_width=FROZEN_STAGE_A_CANVAS_WIDTH,
        canvas_height=FROZEN_STAGE_A_CANVAS_HEIGHT,
        candle_body_width=FROZEN_STAGE_A_CANDLE_BODY_WIDTH,
        candle_gap=FROZEN_STAGE_A_CANDLE_GAP,
        price_label_gutter=FROZEN_STAGE_A_PRICE_LABEL_GUTTER,
    )


def build_frozen_stage_a_stimulus() -> StageAStimulus:
    """Re-render the approved observation with the frozen compact presentation.

    The canonical observation, structured artifact, and OHLC recipe identity come
    directly from ``build_stage_a_stimulus``. Only the visual presentation config
    is replaced, and that replacement becomes part of the frozen visual identity.
    """
    base = build_stage_a_stimulus()
    by_timeframe = {
        timeframe: tuple(bar for bar in base.observation.bars if bar.timeframe == timeframe)
        for timeframe in ("1H", "15m", "5m")
    }
    if tuple(len(by_timeframe[tf]) for tf in ("1H", "15m", "5m")) != (8, 32, 96):
        raise ValueError("Stage-A canonical bar counts drifted before visual freeze")

    rendered = JiangheVisualRenderer(frozen_stage_a_renderer_config()).render(
        VisualObservationSpec(
            product=base.observation.identity.product,
            concrete_contract=base.observation.identity.concrete_contract,
            as_of=base.observation.identity.decision_time,
            panels=(
                VisualPanel("1H", by_timeframe["1H"]),
                VisualPanel("15m", by_timeframe["15m"]),
                VisualPanel("5m", by_timeframe["5m"]),
            ),
        )
    )
    visual = VisualInputArtifact(
        source_observation_identity=base.observation.identity.identity,
        renderer_identity=rendered.renderer_config_identity,
        png_bytes=rendered.png_bytes,
    )
    return StageAStimulus(
        observation=base.observation,
        structured=base.structured,
        visual=visual,
        png_sha256=rendered.png_sha256,
        renderer_config_identity=rendered.renderer_config_identity,
        renderer_input_identity=rendered.input_observation_identity,
        visual_artifact_identity=rendered.visual_artifact_identity,
        recipe_identity=base.recipe_identity,
    )


__all__ = [
    "FROZEN_STAGE_A_CANVAS_HEIGHT",
    "FROZEN_STAGE_A_CANVAS_WIDTH",
    "FROZEN_STAGE_A_CANDLE_BODY_WIDTH",
    "FROZEN_STAGE_A_CANDLE_GAP",
    "FROZEN_STAGE_A_PRICE_LABEL_GUTTER",
    "build_frozen_stage_a_stimulus",
    "frozen_stage_a_renderer_config",
]

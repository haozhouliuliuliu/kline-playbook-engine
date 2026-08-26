"""Provider-smoke visual observation wiring for SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1.

This module is the single, deterministic bridge that turns one governed wake's
causal 4H/1H/15m/5m context bars into exactly four ``image/png`` visual artifacts
using the accepted project renderer (``JiangheVisualRenderer``).  It does not
create a second renderer, does not change timeframe aggregation semantics, and
never looks at a future bar.

Per governed wake it produces:

- 4 deterministic PNG byte streams (one per active timeframe);
- 4 ``ChartRender`` provenance records that are later bound to the formal
  ``JiangheObservation`` identity (so ``visual_artifact_identity``,
  ``source_observation_identity``, ``renderer_config_identity``, PNG SHA-256 and
  ``mime_type = image/png`` all survive into the request context).

The smoke runner uses this same helper for the PNG bytes that are attached to the
Harness one-shot request; the orchestrator uses it for the observation metadata.
Because rendering is pure and deterministic, both derive identical bytes and
identities.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from src.jianghe_ai_trader import ChartRender, ObservationBar
from src.jianghe_visual_renderer import (
    ARTIFACT_KIND,
    PNG_MIME,
    RENDERER_VERSION,
    JiangheVisualRenderer,
    RenderedVisualArtifact,
    VisualObservationSpec,
    VisualPanel,
)

ACTIVE_SMOKE_TIMEFRAMES = ("4H", "1H", "15m", "5m")
SMOKE_CHART_WINDOW_DEFINITION = "CAUSAL_VISIBLE_PANEL_NO_FUTURE"
SMOKE_VISUAL_WIRING_VERSION = "KPE_REPLAY_V0_1_PROVIDER_SMOKE_VISUAL_V0_1"


@dataclass(frozen=True)
class RenderedWakeCharts:
    """Four rendered panels for one governed wake plus their provenance."""

    charts: tuple[ChartRender, ...]
    artifacts: tuple[RenderedVisualArtifact, ...]
    png_bytes: tuple[bytes, ...]
    png_sha256s: tuple[str, ...]

    def __post_init__(self) -> None:
        if len(self.charts) != len(ACTIVE_SMOKE_TIMEFRAMES):
            raise ValueError("provider smoke wake must bind exactly four charts")
        if not (len(self.charts) == len(self.artifacts) == len(self.png_bytes) == len(self.png_sha256s)):
            raise ValueError("rendered wake chart provenance must be internally aligned")
        if tuple(chart.timeframe for chart in self.charts) != ACTIVE_SMOKE_TIMEFRAMES:
            raise ValueError("provider smoke charts must follow 4H/1H/15m/5m order")
        for chart, artifact, png_sha in zip(self.charts, self.artifacts, self.png_sha256s):
            if chart.render_content_hash != png_sha:
                raise ValueError("ChartRender PNG SHA-256 disagrees with rendered artifact")
            if artifact.png_sha256 != png_sha:
                raise ValueError("rendered artifact PNG SHA-256 disagrees with recorded chart")
            if chart.renderer_config_identity != artifact.renderer_config_identity:
                raise ValueError("renderer config identity disagrees between chart and artifact")


def _panel_spec(
    *,
    product: str,
    concrete_contract: str,
    as_of: datetime,
    timeframe: str,
    bars: Sequence[ObservationBar],
) -> VisualObservationSpec:
    """One deterministic single-panel observation spec for one active timeframe."""
    return VisualObservationSpec(
        product=product,
        concrete_contract=concrete_contract,
        as_of=as_of,
        panels=(VisualPanel(timeframe=timeframe, bars=tuple(bars)),),
    )


def render_wake_charts(
    *,
    bars: Sequence[ObservationBar],
    product: str,
    concrete_contract: str,
    as_of: datetime,
    renderer: JiangheVisualRenderer,
) -> RenderedWakeCharts:
    """Deterministically render the causal 4H/1H/15m/5m panels of one wake.

    ``bars`` must already be the causally visible, closed, active-stack context
    for the wake (the orchestrator rejects future bars before this point).  Each
    timeframe is rendered as its own single-panel PNG so a governed wake carries
    exactly four images.
    """
    if not isinstance(renderer, JiangheVisualRenderer):
        raise TypeError("provider smoke visual wiring requires the accepted JiangheVisualRenderer")
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("as_of must be timezone-aware")
    by_timeframe: dict[str, list[ObservationBar]] = {}
    for bar in bars:
        if not isinstance(bar, ObservationBar):
            raise TypeError("bars must contain ObservationBar values")
        by_timeframe.setdefault(bar.timeframe, []).append(bar)
    missing = set(ACTIVE_SMOKE_TIMEFRAMES) - set(by_timeframe)
    if missing:
        raise ValueError(f"provider smoke visual wiring requires the active stack; missing {sorted(missing)}")

    charts: list[ChartRender] = []
    artifacts: list[RenderedVisualArtifact] = []
    png_bytes: list[bytes] = []
    png_sha256s: list[str] = []

    for timeframe in ACTIVE_SMOKE_TIMEFRAMES:
        tf_bars = tuple(sorted(by_timeframe[timeframe], key=lambda bar: bar.open_time))
        spec = _panel_spec(
            product=product,
            concrete_contract=concrete_contract,
            as_of=as_of,
            timeframe=timeframe,
            bars=tf_bars,
        )
        artifact = renderer.render(spec)
        png_sha = artifact.png_sha256
        chart = ChartRender(
            renderer_identity=RENDERER_VERSION,
            timeframe=timeframe,
            window_definition=SMOKE_CHART_WINDOW_DEFINITION,
            current_time=as_of,
            render_content_hash=png_sha,
            partial_bar_marked=False,
            renderer_config_identity=artifact.renderer_config_identity,
            artifact_kind=ARTIFACT_KIND,
            mime_type=PNG_MIME,
        )
        charts.append(chart)
        artifacts.append(artifact)
        png_bytes.append(artifact.png_bytes)
        png_sha256s.append(png_sha)

    return RenderedWakeCharts(
        charts=tuple(charts),
        artifacts=tuple(artifacts),
        png_bytes=tuple(png_bytes),
        png_sha256s=tuple(png_sha256s),
    )


__all__ = [
    "ACTIVE_SMOKE_TIMEFRAMES",
    "RenderedWakeCharts",
    "SMOKE_CHART_WINDOW_DEFINITION",
    "SMOKE_VISUAL_WIRING_VERSION",
    "render_wake_charts",
]

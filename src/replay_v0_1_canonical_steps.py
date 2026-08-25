"""Bridge canonical fixed-5m replay bars into governed replay wake steps.

This module is deliberately semantic-neutral about higher-timeframe construction.
It converts the already-governed canonical 5m wake bar into ``ObservationBar``
and validates caller-supplied causal 4H/1H/15m/5m context before creating the
existing ``GovernedWakeStep``.  It does not choose 15m/1H/4H bucket anchors.

That separation is intentional: exact higher-timeframe bucket anchoring is an
outcome-affecting observation rule and is not silently invented here.
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from decimal import Decimal

from src.jianghe_ai_trader import ObservationBar
from src.replay_v0_1_canonical_feed import (
    CanonicalFiveMinutePreflight,
    ReplayFiveMinuteBar,
)
from src.replay_v0_1_orchestrator import GovernedWakeStep

ACTIVE_TIMEFRAMES = frozenset({"4H", "1H", "15m", "5m"})
CANONICAL_STEP_ADAPTER_VERSION = "KPE_REPLAY_V0_1_CANONICAL_STEP_ADAPTER_V0_1"


def _decimal_text(value: Decimal) -> str:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ValueError("canonical OHLCV must be finite Decimal values")
    if value == 0:
        return "0"
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def canonical_5m_to_observation_bar(bar: ReplayFiveMinuteBar) -> ObservationBar:
    """Losslessly project one governed canonical 5m bar into observation shape."""
    if not isinstance(bar, ReplayFiveMinuteBar):
        raise TypeError("bar must be ReplayFiveMinuteBar")
    return ObservationBar(
        timeframe="5m",
        open_time=bar.start,
        close_time=bar.end,
        available_at=bar.available_at,
        open_price=_decimal_text(bar.open),
        high_price=_decimal_text(bar.high),
        low_price=_decimal_text(bar.low),
        close_price=_decimal_text(bar.close),
        volume=_decimal_text(bar.volume),
        is_closed=True,
    )


@dataclass(frozen=True)
class CanonicalSessionWakeBars:
    """One official governed session window and its ordered fixed-5m wake bars."""

    trading_day: object
    session_identity: str
    wake_bars: tuple[ReplayFiveMinuteBar, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.session_identity, str) or not self.session_identity:
            raise ValueError("session_identity must be non-empty")
        if not self.wake_bars:
            raise ValueError("canonical governed session must contain wake bars")
        if any(item.session_window_identity != self.session_identity for item in self.wake_bars):
            raise ValueError("canonical session group mixes session-window identities")
        if any(item.trading_day != self.trading_day for item in self.wake_bars):
            raise ValueError("canonical session group mixes trading days")
        starts = tuple(item.start for item in self.wake_bars)
        if starts != tuple(sorted(set(starts))):
            raise ValueError("canonical session wake bars must be strictly increasing and unique")


def sessionize_preflight(preflight: CanonicalFiveMinutePreflight) -> tuple[CanonicalSessionWakeBars, ...]:
    """Group preflight wakes by the already-sealed official session-window identity."""
    if not isinstance(preflight, CanonicalFiveMinutePreflight):
        raise TypeError("preflight must be CanonicalFiveMinutePreflight")
    by_identity: dict[str, list[ReplayFiveMinuteBar]] = {}
    order: list[str] = []
    for wake in preflight.wake_bars:
        identity = wake.session_window_identity
        if identity not in by_identity:
            by_identity[identity] = []
            order.append(identity)
        by_identity[identity].append(wake)
    groups = tuple(
        CanonicalSessionWakeBars(
            trading_day=by_identity[identity][0].trading_day,
            session_identity=identity,
            wake_bars=tuple(by_identity[identity]),
        )
        for identity in order
    )
    expected = tuple(window.identity for window in preflight.windows)
    actual = tuple(group.session_identity for group in groups)
    if actual != expected:
        raise ValueError("canonical wake/session ordering drifted from governed preflight windows")
    return groups


def build_governed_wake_step(
    wake_bar: ReplayFiveMinuteBar,
    *,
    context_bars: Sequence[ObservationBar],
) -> GovernedWakeStep:
    """Create one replay step only after a full causal active-stack context exists.

    The caller owns higher-timeframe construction.  This function only validates
    that the supplied context is closed, causal, contains the active timeframe
    stack, and includes the exact canonical wake bar as the newest 5m bar.
    """
    wake_observation = canonical_5m_to_observation_bar(wake_bar)
    context = tuple(context_bars)
    if not context:
        raise ValueError("governed wake context cannot be empty")
    timeframes = {item.timeframe for item in context}
    if not timeframes.issuperset(ACTIVE_TIMEFRAMES):
        raise ValueError(
            "governed wake context must expose 4H/1H/15m/5m before orchestration; "
            f"got {sorted(timeframes)}"
        )
    for item in context:
        if not isinstance(item, ObservationBar):
            raise TypeError("context_bars must contain ObservationBar values")
        if not item.is_closed:
            raise ValueError("V0.1 governed replay context admits only closed bars")
        if item.available_at > wake_observation.available_at:
            raise ValueError("future context availability exceeds the governed wake time")
        if item.close_time > wake_observation.available_at:
            raise ValueError("future context close exceeds the governed wake time")
    same_close_5m = tuple(
        item for item in context
        if item.timeframe == "5m" and item.close_time == wake_observation.close_time
    )
    if same_close_5m != (wake_observation,):
        raise ValueError("context must contain exactly the canonical wake 5m bar at wake close")
    return GovernedWakeStep(
        trading_day=wake_bar.trading_day,
        session_identity=wake_bar.session_window_identity,
        wake_bar=wake_observation,
        context_bars=context,
    )


ContextBuilder = Callable[
    [ReplayFiveMinuteBar, tuple[ReplayFiveMinuteBar, ...]],
    Sequence[ObservationBar],
]


def build_governed_session_steps(
    session: CanonicalSessionWakeBars,
    *,
    context_builder: ContextBuilder,
) -> tuple[GovernedWakeStep, ...]:
    """Apply an explicitly supplied causal context builder to one governed session.

    ``visible_5m_history`` passed to the builder is prefix-only, ending at the
    current wake.  No future canonical 5m bar is exposed through this seam.
    """
    if not isinstance(session, CanonicalSessionWakeBars):
        raise TypeError("session must be CanonicalSessionWakeBars")
    if not callable(context_builder):
        raise TypeError("context_builder must be callable")
    steps: list[GovernedWakeStep] = []
    history: list[ReplayFiveMinuteBar] = []
    for wake in session.wake_bars:
        history.append(wake)
        visible = tuple(history)
        context = context_builder(wake, visible)
        steps.append(build_governed_wake_step(wake, context_bars=context))
    return tuple(steps)


__all__ = [
    "ACTIVE_TIMEFRAMES",
    "CANONICAL_STEP_ADAPTER_VERSION",
    "CanonicalSessionWakeBars",
    "ContextBuilder",
    "build_governed_session_steps",
    "build_governed_wake_step",
    "canonical_5m_to_observation_bar",
    "sessionize_preflight",
]

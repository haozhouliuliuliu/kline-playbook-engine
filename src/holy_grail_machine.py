"""Holy Grail V0.4 deterministic machine operationalization.

This module is the MACHINE OPERATIONALIZATION layer for the Holy Grail V0.4
Playbook Contract draft.  It implements ONLY the Owner-approved binding
machine conventions recorded in
``docs/evidence/HOLY_GRAIL_MACHINE_OPERATIONALIZATION_OWNER_APPROVAL_2026-08-21.md``:

- BASE_TO_MACHINE_INTERVAL = 1_MINUTE (PROJECT_INFERRED; zero aggregation, native
  1-minute canonical substrate; 30/60/120 minute remain source alternatives only);
- ADX_RISING_WINDOW = 1_STEP (PROJECT_INFERRED_VERSIONED_NON_OUTCOME);
- SWING_CONFIRMATION_COUNTS = L1_R1 (PROJECT_INFERRED_VERSIONED_NON_OUTCOME);
- TRAILING_STOP_MACHINE_DEFINITION = SWING_BASED_TRAILING, TRAILING_CLASSIFICATION =
  PROJECT_INFERRED, MONOTONIC_TIGHTEN_ONLY = YES.

The module REUSES the existing generic components:
- ``src.technical_features``  : session-authority 1-minute aggregation, Decimal /
  6dp ROUND_HALF_UP FeatureNumericPolicy, Wilder ADX, SMA-seeded EMA, point-in-time
  feature identity;
- ``src.stop_order_execution``: completed-bar conservative stop trigger + minimal
  OCO lifecycle;
- ``src.data_substrate`` / ``src.historical_data``: CompletedBar / SessionMetadata /
  NormalizedHistoricalBar chronology semantics.

It deliberately does NOT create any candidate outcome / PnL / Sharpe / win-rate /
validation / final-holdout / shadow / forward result.  It is a deterministic,
source-faithful, project-inferred machine convention with full identity binding.

Layer boundary (frozen protocol v1.0):
    SOURCE CLAIM != PROJECT INTERPRETATION != MACHINE OPERATIONALIZATION
Every semantic below is a project-inferred machine convention, never a source claim.

Long/short symmetry: the source's PRIMARY plan is the 4-step long rule set
("sells reversed" mirrors it).  The machine evaluates exactly one side per run
(``side="LONG"`` or ``side="SHORT"``) and mirrors every rule deterministically:
long  = buy stop above previous-bar high; protective sell stop at swing low;
        swing trailing raises the stop only.
short = sell stop below previous-bar low; protective buy stop at swing high;
        swing trailing lowers the stop only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path

from src.strategy_evidence import ArtifactBinding
from src.technical_features import (
    ADXValue,
    AggregationResult,
    FEATURE_IMPLEMENTATION_BINDING,
    FeatureNumericPolicy,
    FeatureValue,
    TimeframeSpec,
    compute_adx,
    compute_ema,
)

MACHINE_SCHEMA_VERSION = "holy-grail-machine-v0.4"
HOLY_GRAIL_MACHINE_FEATURE_VERSION = "holy-grail-machine-v0.4"
STATUS_READY = "READY"


def _canonical_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _require_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")


MACHINE_IMPLEMENTATION_BINDING = ArtifactBinding.from_file(
    artifact_kind="code",
    artifact_reference="src/holy_grail_machine.py",
    path=str(Path(__file__).resolve()),
    declared_version=MACHINE_SCHEMA_VERSION,
)


@dataclass(frozen=True)
class HolyGrailMachineParameters:
    """Machine-readable, identity-bound Holy Grail V0.4 parameters.

    Every bound value is a PROJECT INFERRED machine convention (or a
    PROJECT_INFERRED_VERSIONED_NON_OUTCOME choice).  None is a source claim.
    ``identity_id`` binds the full parameter set so any future version change
    produces a distinct identity.
    """

    base_timeframe: str = "1MIN"
    ema_period: int = 20
    ema_price_field: str = "close"
    adx_period: int = 14
    adx_threshold: Decimal = Decimal("30")
    adx_rising_window: str = "1_STEP"
    swing_left_count: int = 1
    swing_right_count: int = 1
    trailing_stop: str = "SWING_BASED_TRAILING"
    trailing_classification: str = "PROJECT_INFERRED"
    monotonic_tighten_only: bool = True
    entry_offset_ticks: int = 1  # PROJECT_INFERRED: buy stop strictly above previous-bar high
    numeric_arithmetic: str = "DECIMAL"
    numeric_quantization: str = "6DP_ROUND_HALF_UP"
    ema_seed: str = "SMA"
    adx_initialization: str = "WILDER_SMA_DX"

    def __post_init__(self) -> None:
        if self.base_timeframe != "1MIN":
            raise ValueError("Holy Grail BASE machine interval must be exactly 1MIN")
        if type(self.ema_period) is not int or self.ema_period <= 0:
            raise ValueError("EMA period must be a positive integer")
        if self.ema_price_field not in ("open", "high", "low", "close"):
            raise ValueError("EMA price field must be open, high, low, or close")
        if type(self.adx_period) is not int or self.adx_period <= 0:
            raise ValueError("ADX period must be a positive integer")
        if type(self.adx_threshold) is not Decimal or not self.adx_threshold.is_finite():
            raise ValueError("ADX threshold must be a finite Decimal")
        if self.adx_rising_window != "1_STEP":
            raise ValueError("only the Owner-approved 1_STEP ADX rising window is implemented")
        if (self.swing_left_count, self.swing_right_count) != (1, 1):
            raise ValueError("only the Owner-approved L1_R1 swing confirmation is implemented")
        if self.trailing_stop != "SWING_BASED_TRAILING":
            raise ValueError("only the Owner-approved SWING_BASED_TRAILING is implemented")
        if self.trailing_classification != "PROJECT_INFERRED":
            raise ValueError("trailing classification must be PROJECT_INFERRED")
        if self.monotonic_tighten_only is not True:
            raise ValueError("MONOTONIC_TIGHTEN_ONLY=YES is the binding convention")
        if type(self.entry_offset_ticks) is not int or self.entry_offset_ticks <= 0:
            raise ValueError("entry offset must be a positive whole tick count")
        if self.numeric_arithmetic != "DECIMAL":
            raise ValueError("arithmetic must be DECIMAL")
        if self.numeric_quantization != "6DP_ROUND_HALF_UP":
            raise ValueError("quantization must be 6DP_ROUND_HALF_UP")
        if self.ema_seed != "SMA":
            raise ValueError("EMA seed must be SMA")
        if self.adx_initialization != "WILDER_SMA_DX":
            raise ValueError("ADX initialization must be WILDER_SMA_DX")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "base_timeframe": self.base_timeframe,
                "ema_period": self.ema_period,
                "ema_price_field": self.ema_price_field,
                "adx_period": self.adx_period,
                "adx_threshold": str(self.adx_threshold),
                "adx_rising_window": self.adx_rising_window,
                "swing_left_count": self.swing_left_count,
                "swing_right_count": self.swing_right_count,
                "trailing_stop": self.trailing_stop,
                "trailing_classification": self.trailing_classification,
                "monotonic_tighten_only": self.monotonic_tighten_only,
                "entry_offset_ticks": self.entry_offset_ticks,
                "numeric_arithmetic": self.numeric_arithmetic,
                "numeric_quantization": self.numeric_quantization,
                "ema_seed": self.ema_seed,
                "adx_initialization": self.adx_initialization,
                "schema_version": MACHINE_SCHEMA_VERSION,
            }
        )


class HolyGrailEventType:
    """Deterministic event types emitted by the machine operationalization."""

    CONTEXT_SATISFIED = "CONTEXT_SATISFIED"
    EMA_TOUCH = "EMA_TOUCH"
    ENTRY_ORDER_RESTING = "ENTRY_ORDER_RESTING"
    ENTRY_FILLED = "ENTRY_FILLED"
    ENTRY_AMBIGUOUS_INTRABAR_SEQUENCE = "ENTRY_AMBIGUOUS_INTRABAR_SEQUENCE"
    PROTECTIVE_STOP_PENDING = "PROTECTIVE_STOP_PENDING"
    PROTECTIVE_STOP_ACTIVE = "PROTECTIVE_STOP_ACTIVE"
    SWING_PIVOT_CONFIRMED = "SWING_PIVOT_CONFIRMED"
    STOP_RAISED = "STOP_RAISED"
    STOP_LOWERED = "STOP_LOWERED"
    STOP_TRIGGERED = "STOP_TRIGGERED"
    POSITION_OPENED = "POSITION_OPENED"
    POSITION_CLOSED = "POSITION_CLOSED"
    STOP_REPLACED = "STOP_REPLACED"


@dataclass(frozen=True)
class HolyGrailEvent:
    """One deterministic machine event with full identity binding."""

    event_type: str
    side: str  # LONG | SHORT | NONE
    bar_index: int
    bar_identity: str
    available_at: datetime
    detail: str
    reference_price: Decimal | None = None
    previous_stop_price: Decimal | None = None
    pivot_index: int | None = None

    def __post_init__(self) -> None:
        _require_text(self.event_type, "event type")
        if self.side not in ("LONG", "SHORT", "NONE"):
            raise ValueError("event side must be LONG, SHORT, or NONE")
        if type(self.bar_index) is not int or self.bar_index < 0:
            raise ValueError("event bar index must be a non-negative integer")
        _require_text(self.bar_identity, "event bar identity")
        if self.available_at.tzinfo is None:
            raise ValueError("event availability must be timezone-aware")
        if self.reference_price is not None and (
            type(self.reference_price) is not Decimal
            or not self.reference_price.is_finite()
            or self.reference_price <= 0
        ):
            raise ValueError("event reference price must be a positive finite Decimal")
        if self.previous_stop_price is not None and (
            type(self.previous_stop_price) is not Decimal
            or not self.previous_stop_price.is_finite()
            or self.previous_stop_price <= 0
        ):
            raise ValueError("event previous stop price must be a positive finite Decimal")
        if self.pivot_index is not None and (
            type(self.pivot_index) is not int or self.pivot_index < 0
        ):
            raise ValueError("event pivot index must be a non-negative integer")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "event_type": self.event_type,
                "side": self.side,
                "bar_index": self.bar_index,
                "bar_identity": self.bar_identity,
                "available_at": self.available_at.isoformat(),
                "detail": self.detail,
                "reference_price": None if self.reference_price is None else str(self.reference_price),
                "previous_stop_price": (
                    None if self.previous_stop_price is None else str(self.previous_stop_price)
                ),
                "pivot_index": self.pivot_index,
            }
        )


@dataclass(frozen=True)
class HolyGrailEventSequence:
    """Deterministic ordered event sequence produced by one evaluation."""

    machine_identity: str
    parameter_identity: str
    implementation_artifact_identity: str
    feature_implementation_artifact_identity: str
    ema_feature_version: str
    adx_feature_version: str
    aggregation_stream_identity: str
    timeframe_spec_identity: str
    base_interval_seconds: int
    side: str
    events: tuple[HolyGrailEvent, ...]

    def __post_init__(self) -> None:
        _require_text(self.machine_identity, "machine identity")
        _require_text(self.parameter_identity, "parameter identity")
        _require_text(self.implementation_artifact_identity, "implementation artifact identity")
        _require_text(self.feature_implementation_artifact_identity, "feature artifact identity")
        _require_text(self.ema_feature_version, "EMA feature version")
        _require_text(self.adx_feature_version, "ADX feature version")
        _require_text(self.aggregation_stream_identity, "aggregation stream identity")
        _require_text(self.timeframe_spec_identity, "timeframe spec identity")
        if self.side not in ("LONG", "SHORT"):
            raise ValueError("sequence side must be LONG or SHORT")
        if type(self.base_interval_seconds) is not int or self.base_interval_seconds <= 0:
            raise ValueError("base interval must be positive whole seconds")
        bars = [event.bar_index for event in self.events]
        if any(left > right for left, right in zip(bars, bars[1:])):
            raise ValueError("event sequence bar indexes must be non-decreasing")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "machine_identity": self.machine_identity,
                "parameter_identity": self.parameter_identity,
                "implementation_artifact_identity": self.implementation_artifact_identity,
                "feature_implementation_artifact_identity": self.feature_implementation_artifact_identity,
                "ema_feature_version": self.ema_feature_version,
                "adx_feature_version": self.adx_feature_version,
                "aggregation_stream_identity": self.aggregation_stream_identity,
                "timeframe_spec_identity": self.timeframe_spec_identity,
                "base_interval_seconds": self.base_interval_seconds,
                "side": self.side,
                "events": [event.identity_id for event in self.events],
            }
        )


@dataclass(frozen=True)
class ConfirmedSwingPivot:
    """A confirmed L1_R1 fractal pivot.

    Pivot at index ``pivot_index`` becomes available only after the right-side
    confirmation bar (``pivot_index + right_count``) has completed; same-bar
    availability is NO.
    """

    pivot_index: int
    side: str  # LOW | HIGH
    price: Decimal
    confirmed_at_bar: int  # bar index at which the pivot becomes available
    bar_identity: str

    def __post_init__(self) -> None:
        if self.side not in ("LOW", "HIGH"):
            raise ValueError("pivot side must be LOW or HIGH")
        if type(self.pivot_index) is not int or self.pivot_index < 0:
            raise ValueError("pivot index must be a non-negative integer")
        if type(self.confirmed_at_bar) is not int or self.confirmed_at_bar < 0:
            raise ValueError("pivot confirmed-at bar must be a non-negative integer")
        if self.confirmed_at_bar <= self.pivot_index:
            raise ValueError("pivot cannot be confirmed on or before its own bar")
        if type(self.price) is not Decimal or not self.price.is_finite() or self.price <= 0:
            raise ValueError("pivot price must be a positive finite Decimal")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "pivot_index": self.pivot_index,
                "side": self.side,
                "price": str(self.price),
                "confirmed_at_bar": self.confirmed_at_bar,
                "bar_identity": self.bar_identity,
            }
        )


class HolyGrailMachineOperationalization:
    """Deterministic completed-bar Holy Grail V0.4 engine.

    Reuses the generic feature/aggregation/stop components; implements only the
    Owner-approved Holy Grail machine conventions.  Evaluates exactly one side
    (LONG or SHORT) per run with full long/short mirror symmetry.  Produces a
    deterministic event sequence with full identity binding.  No candidate
    outcome is produced.
    """

    def __init__(
        self,
        parameters: HolyGrailMachineParameters,
        numeric_policy: FeatureNumericPolicy,
        *,
        exchange: str,
        concrete_instrument: str,
        tick_size: Decimal,
        side: str = "LONG",
    ) -> None:
        if not isinstance(parameters, HolyGrailMachineParameters):
            raise ValueError("machine requires HolyGrailMachineParameters")
        if not isinstance(numeric_policy, FeatureNumericPolicy):
            raise ValueError("machine requires an explicit FeatureNumericPolicy")
        _require_text(exchange, "exchange")
        _require_text(concrete_instrument, "concrete instrument")
        if type(tick_size) is not Decimal or not tick_size.is_finite() or tick_size <= 0:
            raise ValueError("tick size must be a positive finite Decimal")
        if side not in ("LONG", "SHORT"):
            raise ValueError("machine side must be LONG or SHORT")
        self.parameters = parameters
        self.numeric_policy = numeric_policy
        self.exchange = exchange
        self.concrete_instrument = concrete_instrument
        self.tick_size = tick_size
        self.side = side

    @property
    def machine_identity(self) -> str:
        return _canonical_hash(
            {
                "parameter_identity": self.parameters.identity_id,
                "implementation_artifact_identity": MACHINE_IMPLEMENTATION_BINDING.identity_id,
                "feature_implementation_artifact_identity": FEATURE_IMPLEMENTATION_BINDING.identity_id,
                "exchange": self.exchange,
                "concrete_instrument": self.concrete_instrument,
                "tick_size": str(self.tick_size),
                "side": self.side,
                "schema_version": MACHINE_SCHEMA_VERSION,
            }
        )

    # ---- feature / chronology helpers -------------------------------------

    def _ema_ready(self, ema: tuple[FeatureValue, ...], index: int) -> Decimal | None:
        if index < 0 or index >= len(ema):
            return None
        value = ema[index]
        if value.status != STATUS_READY or value.value is None:
            return None
        return value.value

    def _adx_ready(self, adx: tuple[ADXValue, ...], index: int) -> Decimal | None:
        if index < 0 or index >= len(adx):
            return None
        value = adx[index]
        if value.status != STATUS_READY or value.adx is None:
            return None
        return value.adx

    def _touch(self, bar_low: Decimal, bar_high: Decimal, ema_prior: Decimal) -> bool:
        # TOUCH_RULE=BAR_LOW_LE_EMA_PRIOR_LE_BAR_HIGH; EMA_REFERENCE=PRIOR_COMPLETED_BAR_AVAILABLE
        return bar_low <= ema_prior <= bar_high

    def _adx_context(self, adx: tuple[ADXValue, ...], context_index: int) -> bool:
        # Initial pre-pullback context bar: ADX > threshold AND 1-step rising.
        current = self._adx_ready(adx, context_index)
        previous = self._adx_ready(adx, context_index - 1)
        if current is None or previous is None:
            return False
        return current > self.parameters.adx_threshold and current > previous

    def _is_pivot(self, bars, t: int) -> str | None:
        """L1_R1 fractal pivot at ``t``.  Strict comparisons only; an equal
        neighbour does NOT confirm a pivot (deterministic equal-edge behavior)."""
        params = self.parameters
        left = t - params.swing_left_count
        right = t + params.swing_right_count
        if left < 0 or right >= len(bars):
            return None
        bar = bars[t]
        if bar.low < bars[t - 1].low and bar.low < bars[t + 1].low:
            return "LOW"
        if bar.high > bars[t - 1].high and bar.high > bars[t + 1].high:
            return "HIGH"
        return None

    def _confirm_swing_pivots(
        self, bars, start_index: int, end_index: int
    ) -> tuple[ConfirmedSwingPivot, ...]:
        """Pivots whose confirmation bar lies in ``[start_index, end_index]``."""
        params = self.parameters
        pivots: list[ConfirmedSwingPivot] = []
        for t in range(max(1, start_index - params.swing_right_count), len(bars) - 1):
            confirmed_at = t + params.swing_right_count
            if confirmed_at > end_index or confirmed_at >= len(bars):
                continue
            pivot_side = self._is_pivot(bars, t)
            if pivot_side is None:
                continue
            bar = bars[t]
            price = bar.low if pivot_side == "LOW" else bar.high
            pivots.append(
                ConfirmedSwingPivot(
                    pivot_index=t,
                    side=pivot_side,
                    price=price,
                    confirmed_at_bar=confirmed_at,
                    bar_identity=bar.identity_id,
                )
            )
        return tuple(sorted(pivots, key=lambda item: (item.confirmed_at_bar, item.pivot_index)))

    # ---- evaluation -------------------------------------------------------

    def evaluate(self, aggregation: AggregationResult) -> HolyGrailEventSequence:
        if not isinstance(aggregation, AggregationResult):
            raise ValueError("machine evaluation requires an AggregationResult")
        if not aggregation.complete:
            raise ValueError("machine evaluation requires a complete aggregation (no gaps)")
        spec: TimeframeSpec = aggregation.timeframe_spec
        if spec.kind != "INTRADAY" or spec.interval_seconds != 60:
            raise ValueError("Holy Grail BASE machine interval must be exactly 1-minute (60s)")
        if aggregation.concrete_instrument != self.concrete_instrument:
            raise ValueError("aggregation concrete instrument disagrees with machine binding")
        if aggregation.exchange != self.exchange:
            raise ValueError("aggregation exchange disagrees with machine binding")

        bars = aggregation.aggregates
        if len(bars) < 2:
            raise ValueError("machine evaluation requires at least two completed bars")

        ema = compute_ema(
            aggregation,
            period=self.parameters.ema_period,
            price_field=self.parameters.ema_price_field,
            numeric_policy=self.numeric_policy,
            feature_version=HOLY_GRAIL_MACHINE_FEATURE_VERSION,
        )
        adx = compute_adx(
            aggregation,
            period=self.parameters.adx_period,
            numeric_policy=self.numeric_policy,
            feature_version=HOLY_GRAIL_MACHINE_FEATURE_VERSION,
        )

        events: list[HolyGrailEvent] = []
        state = {
            "side": self.side,
            "entry_fill_bar": None,
            "entry_stop_price": None,
            "entry_stop_resting_from": None,
            "protective_stop_price": None,
            "protective_stop_side": None,
            "protective_stop_pending": False,
            "position_open_price": None,
            "last_processed_pivot": None,
            "stopped_out": False,
        }

        def emit(
            event_type: str,
            bar_index: int,
            side: str,
            detail: str,
            reference_price: Decimal | None = None,
            previous_stop_price: Decimal | None = None,
            pivot_index: int | None = None,
        ) -> None:
            bar = bars[bar_index]
            events.append(
                HolyGrailEvent(
                    event_type=event_type,
                    side=side,
                    bar_index=bar_index,
                    bar_identity=bar.identity_id,
                    available_at=bar.available_at,
                    detail=detail,
                    reference_price=reference_price,
                    previous_stop_price=previous_stop_price,
                    pivot_index=pivot_index,
                )
            )

        for index in range(1, len(bars)):
            bar = bars[index]
            newly_confirmed = self._confirm_swing_pivots(
                bars, start_index=index, end_index=index
            )
            for pivot in newly_confirmed:
                emit(
                    HolyGrailEventType.SWING_PIVOT_CONFIRMED,
                    index,
                    "NONE",
                    f"confirmed L1_R1 {pivot.side.lower()} pivot at bar {pivot.pivot_index}",
                    reference_price=pivot.price,
                    pivot_index=pivot.pivot_index,
                )

            if state["stopped_out"]:
                continue

            if state["entry_fill_bar"] is None:
                self._advance_pre_fill(
                    bars=bars,
                    ema=ema,
                    adx=adx,
                    index=index,
                    state=state,
                    emit=emit,
                )
            else:
                self._advance_in_position(
                    bars=bars,
                    index=index,
                    state=state,
                    emit=emit,
                    newly_confirmed=newly_confirmed,
                )

        sequence = HolyGrailEventSequence(
            machine_identity=self.machine_identity,
            parameter_identity=self.parameters.identity_id,
            implementation_artifact_identity=MACHINE_IMPLEMENTATION_BINDING.identity_id,
            feature_implementation_artifact_identity=FEATURE_IMPLEMENTATION_BINDING.identity_id,
            ema_feature_version=HOLY_GRAIL_MACHINE_FEATURE_VERSION,
            adx_feature_version=HOLY_GRAIL_MACHINE_FEATURE_VERSION,
            aggregation_stream_identity=aggregation.feature_stream_identity,
            timeframe_spec_identity=spec.identity_id,
            base_interval_seconds=60,
            side=self.side,
            events=tuple(events),
        )
        return sequence

    def _entry_stop_levels(self, prior) -> tuple[Decimal, Decimal]:
        """(long_stop, short_stop) for the bar preceding the touch bar."""
        long_stop = prior.high + self.tick_size
        short_stop = prior.low - self.tick_size
        return long_stop, short_stop

    def _advance_pre_fill(self, *, bars, ema, adx, index, state, emit) -> None:
        """Flat state: EMA touch + ADX context -> resting entry stop.

        Completed-bar conservative chronology: the touch is observed only at the
        touch bar's completion; the entry stop rests from the NEXT bar.  If the
        touch bar itself already crossed the entry stop level, the ordering of
        touch vs entry-stop within that bar is not observable at 1-minute
        resolution and the attempt fails closed (GATE-04)."""
        bar = bars[index]
        prior = bars[index - 1]

        # A resting entry order from a previous touch may still fill on this bar.
        if state["entry_stop_price"] is not None:
            self._maybe_fill_entry(bars=bars, index=index, state=state, emit=emit)
            return

        ema_prior = self._ema_ready(ema, index - 1)
        if ema_prior is None:
            return
        if not self._touch(bar.low, bar.high, ema_prior):
            return
        if not self._adx_context(adx, index - 1):
            return

        emit(
            HolyGrailEventType.CONTEXT_SATISFIED,
            index,
            "NONE",
            "ADX>30 and 1-step rising observed at initial pre-pullback context bar (bar "
            + str(index - 1) + ")",
        )
        emit(
            HolyGrailEventType.EMA_TOUCH,
            index,
            "NONE",
            "EMA20 touch by bar range against prior completed-bar EMA",
        )

        long_stop, short_stop = self._entry_stop_levels(prior)
        if self.side == "LONG":
            if bar.high >= long_stop:
                emit(
                    HolyGrailEventType.ENTRY_AMBIGUOUS_INTRABAR_SEQUENCE,
                    index,
                    "LONG",
                    "EMA touch and buy-stop threshold reached in the same bar; ordering unobservable at 1m",
                )
                return
            state["entry_stop_price"] = long_stop
        else:
            if bar.low <= short_stop:
                emit(
                    HolyGrailEventType.ENTRY_AMBIGUOUS_INTRABAR_SEQUENCE,
                    index,
                    "SHORT",
                    "EMA touch and sell-stop threshold reached in the same bar; ordering unobservable at 1m",
                )
                return
            state["entry_stop_price"] = short_stop
        state["entry_stop_resting_from"] = index + 1
        state["entry_fill_bar"] = None
        emit(
            HolyGrailEventType.ENTRY_ORDER_RESTING,
            index,
            self.side,
            (
                "buy stop above previous-bar high (prior high + 1 tick)"
                if self.side == "LONG"
                else "sell stop below previous-bar low (prior low - 1 tick)"
            ),
            reference_price=state["entry_stop_price"],
        )

    def _maybe_fill_entry(self, *, bars, index, state, emit) -> None:
        if index < state["entry_stop_resting_from"]:
            return
        entry_stop = state["entry_stop_price"]
        bar = bars[index]
        filled = False
        if self.side == "LONG" and bar.high >= entry_stop:
            filled = True
        elif self.side == "SHORT" and bar.low <= entry_stop:
            filled = True
        if not filled:
            return
        state["entry_fill_bar"] = index
        state["position_open_price"] = entry_stop
        emit(
            HolyGrailEventType.ENTRY_FILLED,
            index,
            self.side,
            f"{'buy' if self.side == 'LONG' else 'sell'} stop filled (reference price = entry stop)",
            reference_price=entry_stop,
        )
        emit(
            HolyGrailEventType.POSITION_OPENED,
            index,
            self.side,
            f"{self.side.lower()} position opened",
            reference_price=entry_stop,
        )
        self._bind_or_defer_initial_stop(bars=bars, index=index, state=state, emit=emit)

    def _advance_in_position(self, *, bars, index, state, emit, newly_confirmed) -> None:
        self._manage_protective_stop(
            bars=bars,
            index=index,
            state=state,
            emit=emit,
            newly_confirmed=newly_confirmed,
        )

    def _bind_or_defer_initial_stop(self, *, bars, index, state, emit) -> None:
        """Bind the initial protective stop to the newly formed swing low/high.

        Honest stop-activation latency: if no confirmed L1_R1 pivot is available
        at the entry-fill bar, the protective stop is PENDING until the first
        confirmed pivot appears.  No 'entry always has a stop' claim is made."""
        side = self.side
        want = "LOW" if side == "LONG" else "HIGH"
        available = [
            pivot
            for pivot in self._confirm_swing_pivots(bars, start_index=0, end_index=index)
            if pivot.side == want
        ]
        if not available:
            state["protective_stop_pending"] = True
            emit(
                HolyGrailEventType.PROTECTIVE_STOP_PENDING,
                index,
                side,
                "no confirmed swing pivot available at entry; protective stop pending (stop-activation latency)",
            )
            return
        pivot = max(available, key=lambda item: item.pivot_index)
        stop_price = pivot.price
        stop_side = "SELL_STOP" if side == "LONG" else "BUY_STOP"
        state["protective_stop_price"] = stop_price
        state["protective_stop_side"] = stop_side
        state["protective_stop_pending"] = False
        state["last_processed_pivot"] = pivot.pivot_index
        emit(
            HolyGrailEventType.PROTECTIVE_STOP_ACTIVE,
            index,
            side,
            f"initial protective stop at newly formed confirmed swing {'low' if side == 'LONG' else 'high'}",
            reference_price=stop_price,
            pivot_index=pivot.pivot_index,
        )

    def _manage_protective_stop(self, *, bars, index, state, emit, newly_confirmed) -> None:
        """Protective stop trigger check + swing-based trailing (monotonic only).

        Stop replacement / OCO interaction: a trailing improvement replaces the
        resting protective stop at a strictly better level (recorded as
        STOP_RAISED / STOP_LOWERED / STOP_REPLACED).  The old stop is never
        loosened; a worse pivot is ignored; the same pivot is not reprocessed."""
        side = self.side
        current_stop = state["protective_stop_price"]

        for pivot in newly_confirmed:
            usable = (side == "LONG" and pivot.side == "LOW") or (
                side == "SHORT" and pivot.side == "HIGH"
            )
            if not usable:
                continue
            if state["last_processed_pivot"] == pivot.pivot_index:
                continue
            if current_stop is None:
                # Pending initial stop resolves at the first usable pivot.
                stop_price = pivot.price
                state["protective_stop_price"] = stop_price
                state["protective_stop_pending"] = False
                state["last_processed_pivot"] = pivot.pivot_index
                emit(
                    HolyGrailEventType.PROTECTIVE_STOP_ACTIVE,
                    index,
                    side,
                    "initial protective stop resolved from first confirmed pivot",
                    reference_price=stop_price,
                    pivot_index=pivot.pivot_index,
                )
                current_stop = stop_price
                continue
            # MONOTONIC_TIGHTEN_ONLY: long stop only rises; short stop only falls.
            better_long = side == "LONG" and pivot.price > current_stop
            better_short = side == "SHORT" and pivot.price < current_stop
            if better_long or better_short:
                previous = current_stop
                state["protective_stop_price"] = pivot.price
                state["last_processed_pivot"] = pivot.pivot_index
                event_type = (
                    HolyGrailEventType.STOP_RAISED
                    if side == "LONG"
                    else HolyGrailEventType.STOP_LOWERED
                )
                emit(
                    event_type,
                    index,
                    side,
                    "swing-based trailing stop update (monotonic tighten only; old stop replaced)",
                    reference_price=pivot.price,
                    previous_stop_price=previous,
                    pivot_index=pivot.pivot_index,
                )
                emit(
                    HolyGrailEventType.STOP_REPLACED,
                    index,
                    side,
                    "resting protective stop replaced at a strictly better level",
                    reference_price=pivot.price,
                    previous_stop_price=previous,
                    pivot_index=pivot.pivot_index,
                )
                current_stop = pivot.price

        if state["protective_stop_price"] is None:
            return
        stop_price = state["protective_stop_price"]
        bar = bars[index]
        if side == "LONG" and bar.low <= stop_price:
            emit(
                HolyGrailEventType.STOP_TRIGGERED,
                index,
                side,
                "long protective stop triggered",
                reference_price=stop_price,
            )
            emit(
                HolyGrailEventType.POSITION_CLOSED,
                index,
                side,
                "long position closed at protective stop",
                reference_price=stop_price,
            )
            state["stopped_out"] = True
            return
        if side == "SHORT" and bar.high >= stop_price:
            emit(
                HolyGrailEventType.STOP_TRIGGERED,
                index,
                side,
                "short protective stop triggered",
                reference_price=stop_price,
            )
            emit(
                HolyGrailEventType.POSITION_CLOSED,
                index,
                side,
                "short position closed at protective stop",
                reference_price=stop_price,
            )
            state["stopped_out"] = True
            return

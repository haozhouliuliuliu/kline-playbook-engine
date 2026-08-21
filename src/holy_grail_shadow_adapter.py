"""Holy Grail V0.4 machine-event adapter for the generic synthetic runtime.

The adapter's seam is deliberately small: evaluate one complete, governed 1m
aggregation through the real machine, then expose deterministic directives and
OPEN/CLOSE intents only when their completed-bar evidence is available.  It
does not invent intrabar order chronology.  Stop/OCO directives remain explicit
audit facts so a future broker-order capability cannot silently discard them.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from hashlib import sha256
import json

from src.contract_semantics import PositionDirection
from src.holy_grail_machine import HolyGrailEvent, HolyGrailEventSequence, HolyGrailEventType, HolyGrailMachineOperationalization
from src.intent import IntentAction, StrategyIntent
from src.market_context import MarketContext
from src.technical_features import AggregationResult


def _hash(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class HolyGrailRuntimeDirective:
    """A lossless machine event projection for runtime audit and later OMS support."""

    event_type: str
    available_at: datetime
    reference_price: Decimal | None
    previous_stop_price: Decimal | None
    oco_group_id: str | None
    machine_event_identity: str
    strategy_identity_id: str
    concrete_contract_id: str
    direction: PositionDirection
    quantity: Decimal

    @property
    def identity_id(self) -> str:
        return _hash({"event_type": self.event_type, "available_at": self.available_at.isoformat(), "reference_price": None if self.reference_price is None else str(self.reference_price), "previous_stop_price": None if self.previous_stop_price is None else str(self.previous_stop_price), "oco_group_id": self.oco_group_id, "machine_event_identity": self.machine_event_identity, "strategy_identity_id": self.strategy_identity_id, "concrete_contract_id": self.concrete_contract_id, "direction": self.direction.value, "quantity": str(self.quantity)})


class HolyGrailShadowAdapter:
    """Adapter satisfying ``ShadowRuntime``'s strategy seam with real HG events."""

    def __init__(self, *, sequence: HolyGrailEventSequence, strategy_identity_id: str, instrument: str, concrete_contract_id: str, quantity: Decimal) -> None:
        if not isinstance(sequence, HolyGrailEventSequence):
            raise ValueError("Holy Grail adapter requires a machine event sequence")
        if not all(isinstance(value, str) and value.strip() for value in (strategy_identity_id, instrument, concrete_contract_id)):
            raise ValueError("Holy Grail adapter requires identity bindings")
        if type(quantity) is not Decimal or not quantity.is_finite() or quantity <= 0:
            raise ValueError("Holy Grail adapter requires a positive synthetic quantity")
        self._sequence, self._strategy, self._instrument, self._contract, self._quantity = sequence, strategy_identity_id, instrument, concrete_contract_id, quantity
        self._directives = tuple(self._to_directive(event) for event in sequence.events)

    @classmethod
    def from_machine(cls, *, machine: HolyGrailMachineOperationalization, aggregation: AggregationResult, strategy_identity_id: str, instrument: str, quantity: Decimal) -> "HolyGrailShadowAdapter":
        if not isinstance(machine, HolyGrailMachineOperationalization):
            raise ValueError("Holy Grail adapter requires the real machine")
        return cls(sequence=machine.evaluate(aggregation), strategy_identity_id=strategy_identity_id, instrument=instrument, concrete_contract_id=machine.concrete_instrument, quantity=quantity)

    @property
    def sequence_identity(self) -> str:
        return self._sequence.identity_id

    @property
    def directives(self) -> tuple[HolyGrailRuntimeDirective, ...]:
        return self._directives

    def directives_at(self, available_at: datetime) -> tuple[HolyGrailRuntimeDirective, ...]:
        if available_at.tzinfo is None:
            raise ValueError("directive lookup requires a timezone-aware timestamp")
        return tuple(item for item in self._directives if item.available_at == available_at)

    def intents(self, context: MarketContext) -> tuple[StrategyIntent, ...]:
        if context.concrete_contract_id != self._contract or context.instrument != self._instrument:
            return ()
        events = [item for item in self._sequence.events if item.available_at == context.available_at]
        # ShadowRuntime consumes the same machine facts through its execution
        # directive seam.  Returning market intents here would duplicate the
        # entry/exit stop lifecycle and falsely downgrade it to MARKET.
        return ()

    def _direction(self) -> PositionDirection:
        return PositionDirection.LONG if self._sequence.side == "LONG" else PositionDirection.SHORT

    def _intent(self, event: HolyGrailEvent, context: MarketContext, action: IntentAction, direction: PositionDirection, quantity: Decimal | None, reason: str) -> StrategyIntent:
        return StrategyIntent(
            intent_id=_hash({"strategy": self._strategy, "event": event.identity_id, "action": action.value}),
            strategy_identity_id=self._strategy,
            instrument=self._instrument,
            concrete_contract_id=self._contract,
            action=action,
            decision_at=event.available_at,
            context_identity=context.identity_id,
            direction=direction,
            quantity=quantity,
            reason=reason,
        )

    def _to_directive(self, event: HolyGrailEvent) -> HolyGrailRuntimeDirective:
        oco_events = {HolyGrailEventType.PROTECTIVE_STOP_ACTIVE, HolyGrailEventType.STOP_REPLACED, HolyGrailEventType.STOP_TRIGGERED}
        oco_group_id = _hash({"sequence": self._sequence.identity_id, "role": "HOLY_GRAIL_PROTECTIVE_EXIT"}) if event.event_type in oco_events else None
        return HolyGrailRuntimeDirective(event.event_type, event.available_at, event.reference_price, event.previous_stop_price, oco_group_id, event.identity_id, self._strategy, self._contract, self._direction(), self._quantity)

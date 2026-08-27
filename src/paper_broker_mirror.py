"""External PAPER broker-truth mirror.

Unlike the synthetic TradingState accounting model, this mirror never calculates
broker cash, margin, commissions or positions from fills. It accepts only
broker/account snapshots and exposes a deterministic risk/reconciliation view.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from typing import Iterable

from src.broker_adapter import BrokerAccountSnapshot, BrokerOrderSnapshot, BrokerPositionSnapshot
from src.contract_semantics import PositionDirection
from src.runtime_events import BrokerConnectionState

PAPER_BROKER_MIRROR_SCHEMA_VERSION = "KPE_PAPER_BROKER_MIRROR_V0_1"

def _hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()

@dataclass(frozen=True)
class BrokerMirrorAssessment:
    assessed_at: datetime
    ok: bool
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.assessed_at.tzinfo is None:
            raise ValueError("mirror assessment timestamp must be timezone-aware")
        if type(self.ok) is not bool:
            raise ValueError("mirror assessment ok must be bool")
        if self.reasons != tuple(sorted(set(self.reasons))):
            raise ValueError("mirror assessment reasons must be sorted and unique")
        if self.ok != (not self.reasons):
            raise ValueError("mirror assessment ok must match absence of reasons")

    @property
    def identity_id(self) -> str:
        return _hash({
            "schema_version": PAPER_BROKER_MIRROR_SCHEMA_VERSION,
            "assessed_at": self.assessed_at.isoformat(), "ok": self.ok, "reasons": self.reasons,
        })

class PaperBrokerTruthMirror:
    """Latest broker-truth snapshots; no local fill/account inference."""

    def __init__(self, *, broker_id: str) -> None:
        if not isinstance(broker_id, str) or not broker_id.strip():
            raise ValueError("broker mirror requires broker_id")
        self.broker_id = broker_id
        self._connection_state = BrokerConnectionState.DISCONNECTED
        self._account: BrokerAccountSnapshot | None = None
        self._positions: tuple[BrokerPositionSnapshot, ...] = ()
        self._orders: tuple[BrokerOrderSnapshot, ...] = ()
        self._snapshot_at: datetime | None = None

    @property
    def connection_state(self) -> BrokerConnectionState:
        return self._connection_state
    @property
    def account(self) -> BrokerAccountSnapshot | None:
        return self._account
    @property
    def positions(self) -> tuple[BrokerPositionSnapshot, ...]:
        return self._positions
    @property
    def orders(self) -> tuple[BrokerOrderSnapshot, ...]:
        return self._orders
    @property
    def snapshot_at(self) -> datetime | None:
        return self._snapshot_at

    def set_connection_state(self, state: BrokerConnectionState) -> None:
        if not isinstance(state, BrokerConnectionState):
            raise ValueError("mirror connection state must be explicit")
        self._connection_state = state
        if state is not BrokerConnectionState.CONNECTED:
            self.invalidate_truth()

    def invalidate_truth(self) -> None:
        """Discard a snapshot that was not fully reconstructed this cycle.

        Retaining a previous snapshot after a partial refresh could make an
        order gate mistake old broker truth for a fresh reconciliation result.
        """
        self._account = None
        self._positions = ()
        self._orders = ()
        self._snapshot_at = None

    def refresh(self, *, account: BrokerAccountSnapshot, positions: Iterable[BrokerPositionSnapshot],
                orders: Iterable[BrokerOrderSnapshot], observed_at: datetime) -> None:
        if not isinstance(account, BrokerAccountSnapshot):
            raise ValueError("mirror refresh requires BrokerAccountSnapshot")
        if observed_at.tzinfo is None:
            raise ValueError("mirror refresh time must be timezone-aware")
        pos = tuple(positions)
        ords = tuple(orders)
        if any(not isinstance(item, BrokerPositionSnapshot) for item in pos):
            raise ValueError("mirror positions must be BrokerPositionSnapshot values")
        if any(not isinstance(item, BrokerOrderSnapshot) for item in ords):
            raise ValueError("mirror orders must be BrokerOrderSnapshot values")
        if len({(item.concrete_contract_id, item.direction) for item in pos}) != len(pos):
            raise ValueError("mirror rejects duplicate contract/direction positions")
        if len({item.order_id for item in ords}) != len(ords):
            raise ValueError("mirror rejects duplicate broker order ids")
        if any(item.snapshot_at > observed_at for item in (account, *pos, *ords)):
            raise ValueError("broker snapshot cannot come from the future")
        self._account = account
        self._positions = tuple(sorted(pos, key=lambda item: (item.concrete_contract_id, item.direction.value)))
        self._orders = tuple(sorted(ords, key=lambda item: item.order_id))
        # The oldest constituent fact bounds the freshness of the complete
        # account/position/order truth set.  `observed_at` is merely local
        # receipt time and must not disguise an older broker snapshot.
        self._snapshot_at = min(item.snapshot_at for item in (account, *pos, *ords))

    def position_for(self, concrete_contract_id: str, direction: PositionDirection) -> BrokerPositionSnapshot | None:
        for item in self._positions:
            if item.concrete_contract_id == concrete_contract_id and item.direction is direction:
                return item
        return None

    def orders_for_request(self, client_request_id: str) -> tuple[BrokerOrderSnapshot, ...]:
        return tuple(item for item in self._orders if item.client_request_id == client_request_id)

    def assess(self, *, expected_client_request_ids: Iterable[str], assessed_at: datetime,
               max_snapshot_age_seconds: int) -> BrokerMirrorAssessment:
        if assessed_at.tzinfo is None:
            raise ValueError("mirror assessment time must be timezone-aware")
        if type(max_snapshot_age_seconds) is not int or max_snapshot_age_seconds < 0:
            raise ValueError("mirror snapshot age must be a non-negative integer")
        expected = set(expected_client_request_ids)
        if any(not isinstance(item, str) or not item.strip() for item in expected):
            raise ValueError("expected client request ids must be non-empty strings")
        reasons: list[str] = []
        if self._connection_state is not BrokerConnectionState.CONNECTED:
            reasons.append("BROKER_NOT_CONNECTED")
        if self._account is None or self._snapshot_at is None:
            reasons.append("BROKER_SNAPSHOT_MISSING")
        elif (assessed_at - self._snapshot_at).total_seconds() > max_snapshot_age_seconds:
            reasons.append("BROKER_SNAPSHOT_STALE")
        for order in self._orders:
            if order.client_request_id not in expected:
                reasons.append(f"UNKNOWN_BROKER_ORDER:{order.order_id}")
        return BrokerMirrorAssessment(assessed_at=assessed_at, ok=not reasons,
                                      reasons=tuple(sorted(set(reasons))))

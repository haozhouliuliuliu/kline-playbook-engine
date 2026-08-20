"""Crash / restart recovery for the Shadow Runtime Foundation.

Skeleton v1.0 §5: crash/restart must rebuild state from persistent facts plus
broker reconciliation. This module defines:

- ``RuntimePersistedState`` — the deterministic durable projection of
  ``TradingState`` (account, positions, orders, applied broker events, sequence
  high water, ledger tail identity);
- ``capture_persisted_state`` — snapshot a live ``TradingState``;
- ``rebuild_trading_state`` — reconstruct ``TradingState`` from the persisted
  projection, verifying the ledger chain tail matches (fail closed), then
  record a RECOVERY audit record.

For the paper runtime the broker-side durable truth is the deterministic
``PaperBrokerSnapshot`` fixture; after rebuild the pipeline reconciles the
restored local state against that broker snapshot and fails closed on any
mismatch.

No real broker, no network, no real money.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from hashlib import sha256
import json
from typing import Any, Iterable

from src.contract_semantics import ContractSpecification
from src.runtime_events import (
    BrokerConnectionState,
    BrokerEvent,
    BrokerEventViolation,
)
from src.runtime_ledger import RuntimeLedger, RuntimeLedgerRecordKind, ledger_pairs
from src.trading_state import (
    AccountState,
    PositionState,
    RuntimeAccountingAssumptions,
    RuntimeOrderState,
    TradingState,
)

RECOVERY_SCHEMA_VERSION = "shadow-runtime-recovery-v0.1"


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RuntimePersistedState:
    """Deterministic durable projection of TradingState (recovery input)."""

    runtime_id: str
    runtime_version: str
    created_at: datetime
    persisted_at: datetime
    starting_capital: Decimal
    account: AccountState
    positions: tuple[PositionState, ...]
    orders: tuple[RuntimeOrderState, ...]
    applied_events: tuple[BrokerEvent, ...]
    event_violations: tuple[BrokerEventViolation, ...]
    connection_state: BrokerConnectionState
    ledger_tail_identity: str

    def __post_init__(self) -> None:
        if not self.runtime_id or not self.runtime_version:
            raise ValueError("persisted state requires runtime id and version")
        for field in (self.created_at, self.persisted_at):
            if field.tzinfo is None:
                raise ValueError("persisted state timestamps must be timezone-aware")
        if type(self.starting_capital) is not Decimal or not self.starting_capital.is_finite() or self.starting_capital <= 0:
            raise ValueError("persisted state starting capital must be a positive finite Decimal")
        if not isinstance(self.account, AccountState):
            raise ValueError("persisted state requires an AccountState")
        if not isinstance(self.connection_state, BrokerConnectionState):
            raise ValueError("persisted state requires a BrokerConnectionState")
        if len(self.ledger_tail_identity) != 64:
            raise ValueError("persisted state ledger tail identity must be a sha256 hex digest")
        for value in (self.positions, self.orders, self.applied_events, self.event_violations):
            if not isinstance(value, tuple):
                raise ValueError("persisted state collections must be tuples")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "runtime_id": self.runtime_id,
                "runtime_version": self.runtime_version,
                "created_at": self.created_at.isoformat(),
                "persisted_at": self.persisted_at.isoformat(),
                "starting_capital": str(self.starting_capital),
                "account": self.account.identity_id,
                "positions": [item.identity_id for item in self.positions],
                "orders": [item.identity_id for item in self.orders],
                "applied_events": [item.identity_id for item in self.applied_events],
                "event_violations": [item.identity_id for item in self.event_violations],
                "connection_state": self.connection_state.value,
                "ledger_tail_identity": self.ledger_tail_identity,
            }
        )


def capture_persisted_state(state: TradingState, persisted_at: datetime) -> RuntimePersistedState:
    """Snapshot the live ``TradingState`` as a durable recovery input."""
    if not isinstance(state, TradingState):
        raise ValueError("capture requires a TradingState")
    if persisted_at.tzinfo is None:
        raise ValueError("persist timestamp must be timezone-aware")
    return RuntimePersistedState(
        runtime_id=state.runtime_id,
        runtime_version=state.runtime_version,
        created_at=state.created_at,
        persisted_at=persisted_at,
        starting_capital=state.account.starting_capital,
        account=state.account,
        positions=state.positions,
        orders=state.orders,
        applied_events=state.applied_events(),
        event_violations=state.event_violations(),
        connection_state=state.connection_state,
        ledger_tail_identity=state.ledger_tail_identity,
    )


def rebuild_trading_state(
    persisted: RuntimePersistedState,
    *,
    contract_specs: Iterable[ContractSpecification],
    accounting: RuntimeAccountingAssumptions,
    ledger: RuntimeLedger,
    recovery_recorded_at: datetime,
) -> TradingState:
    """Rebuild ``TradingState`` from persisted facts (fail closed on mismatch).

    The supplied ``ledger`` MUST already contain the persisted chain (its tail
    must equal ``persisted.ledger_tail_identity``); otherwise the rebuild fails
    closed rather than silently losing audit history. A RECOVERY record is then
    appended to the ledger.
    """
    if not isinstance(persisted, RuntimePersistedState):
        raise ValueError("rebuild requires a RuntimePersistedState")
    if not isinstance(ledger, RuntimeLedger):
        raise ValueError("rebuild requires a RuntimeLedger")
    if recovery_recorded_at.tzinfo is None:
        raise ValueError("recovery record timestamp must be timezone-aware")
    if ledger.tail_identity != persisted.ledger_tail_identity:
        raise ValueError(
            "RUNTIME_LEDGER_TAIL_MISMATCH: the ledger does not match the persisted "
            "state; fail closed instead of losing audit history"
        )
    restored = TradingState.restore(
        runtime_id=persisted.runtime_id,
        runtime_version=persisted.runtime_version,
        created_at=persisted.created_at,
        starting_capital=persisted.starting_capital,
        contract_specs=contract_specs,
        accounting=accounting,
        ledger=ledger,
        account=persisted.account,
        positions=persisted.positions,
        orders=persisted.orders,
        applied_events=persisted.applied_events,
        event_violations=persisted.event_violations,
        connection_state=persisted.connection_state,
    )
    ledger.append(
        RuntimeLedgerRecordKind.RECOVERY,
        persisted.identity_id,
        ledger_pairs(
            recovery_action="REBUILD_FROM_PERSISTED_STATE",
            runtime_id=persisted.runtime_id,
            persisted_at=persisted.persisted_at.isoformat(),
            restored_tail_identity=persisted.ledger_tail_identity,
        ),
        recovery_recorded_at,
    )
    return restored

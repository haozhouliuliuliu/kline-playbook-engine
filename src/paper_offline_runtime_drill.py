"""Offline-only wrapper around the broker-neutral PAPER runtime coordinator.

This module exists for deterministic fault-injection and regression tests. It
adds an explicit fake-broker gate and fake clock seam, while all startup,
wake/order, broker-truth and cancel-then-replace sequencing lives in
``src.paper_runtime.PaperRuntimeCoordinator``.

No provider, credential, network, external PAPER account or real-money action is
performed by this module.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from src.paper_order_journal import PaperOrderJournal
from src.paper_runtime import (
    JournalManagedPaperBroker,
    PaperOrderPlan,
    PaperRiskPlanner,
    PaperRuntimeCoordinator,
    PaperTrader,
    PaperTraderDecision,
    PaperWakeResult,
)

PAPER_OFFLINE_RUNTIME_DRILL_VERSION = "KPE_PAPER_OFFLINE_RUNTIME_DRILL_V0_1"

# Compatibility names retained for the existing offline/fault-injection suite.
OfflinePaperTraderDecision = PaperTraderDecision
OfflinePaperOrderPlan = PaperOrderPlan
OfflinePaperWakeResult = PaperWakeResult
OfflinePaperTrader = PaperTrader
OfflinePaperRiskPlanner = PaperRiskPlanner


class OfflineJournaledPaperBroker(JournalManagedPaperBroker, Protocol):
    offline_test_only: bool

    def set_observed_at(self, at: datetime) -> None: ...


class _LegacyOfflineBrokerProxy:
    """Expose the old fake's ``journal`` field as the generic journal contract."""

    offline_test_only = True
    journal_managed_execution = True

    def __init__(self, broker: Any, order_journal: PaperOrderJournal) -> None:
        self._broker = broker
        self._order_journal = order_journal

    @property
    def broker_id(self) -> str:
        return self._broker.broker_id

    @property
    def order_journal(self) -> PaperOrderJournal:
        return self._order_journal

    @property
    def connection_state(self):
        return self._broker.connection_state

    def set_observed_at(self, at: datetime) -> None:
        self._broker.set_observed_at(at)

    def connect(self) -> None:
        self._broker.connect()

    def disconnect(self) -> None:
        self._broker.disconnect()

    def submit_order(self, instruction):
        return self._broker.submit_order(instruction)

    def cancel_order(self, order_id: str) -> None:
        self._broker.cancel_order(order_id)

    def fetch_account_snapshot(self):
        return self._broker.fetch_account_snapshot()

    def fetch_position_snapshot(self):
        return self._broker.fetch_position_snapshot()

    def fetch_order_snapshot(self):
        return self._broker.fetch_order_snapshot()


class PaperOfflineRuntimeDrill(PaperRuntimeCoordinator):
    """Fake-only safety shell over the production-capable composition path."""

    def __init__(self, **kwargs: object) -> None:
        broker = kwargs.get("broker")
        if getattr(broker, "offline_test_only", False) is not True:
            raise PermissionError("OFFLINE_PAPER_DRILL_REQUIRES_FAKE_BROKER")
        if not callable(getattr(broker, "set_observed_at", None)):
            raise ValueError("offline drill fake broker requires set_observed_at")
        order_journal = kwargs.get("order_journal")
        if not isinstance(order_journal, PaperOrderJournal):
            raise ValueError("offline drill requires PaperOrderJournal")
        broker_journal = getattr(broker, "order_journal", None)
        if broker_journal is None:
            broker_journal = getattr(broker, "journal", None)
        if broker_journal is not order_journal:
            raise ValueError("PAPER_RUNTIME_BROKER_JOURNAL_MISMATCH")
        if getattr(broker, "order_journal", None) is None:
            kwargs["broker"] = _LegacyOfflineBrokerProxy(broker, order_journal)
        super().__init__(**kwargs)

    def _before_external_action(self, at: datetime, *, action: str) -> None:
        super()._before_external_action(at, action=action)
        # Test-only deterministic clock injection. Real broker adapters do not
        # implement or need this method.
        self.broker.set_observed_at(at)

    def _before_broker_read(self, at: datetime) -> None:
        super()._before_broker_read(at)
        self.broker.set_observed_at(at)


__all__ = [
    "OfflineJournaledPaperBroker",
    "OfflinePaperOrderPlan",
    "OfflinePaperRiskPlanner",
    "OfflinePaperTrader",
    "OfflinePaperTraderDecision",
    "OfflinePaperWakeResult",
    "PAPER_OFFLINE_RUNTIME_DRILL_VERSION",
    "PaperOfflineRuntimeDrill",
]

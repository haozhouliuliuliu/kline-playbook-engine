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
from typing import Protocol

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

    @property
    def order_journal(self) -> PaperOrderJournal: ...

    def set_observed_at(self, at: datetime) -> None: ...


class PaperOfflineRuntimeDrill(PaperRuntimeCoordinator):
    """Fake-only safety shell over the production-capable composition path."""

    def __init__(self, **kwargs: object) -> None:
        broker = kwargs.get("broker")
        if getattr(broker, "offline_test_only", False) is not True:
            raise PermissionError("OFFLINE_PAPER_DRILL_REQUIRES_FAKE_BROKER")
        if not callable(getattr(broker, "set_observed_at", None)):
            raise ValueError("offline drill fake broker requires set_observed_at")
        super().__init__(**kwargs)

    def _before_external_action(self, at: datetime) -> None:
        super()._before_external_action(at)
        # Test-only deterministic clock injection. Real broker adapters do not
        # implement or need this method.
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

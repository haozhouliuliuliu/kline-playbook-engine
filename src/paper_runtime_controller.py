"""Smallest local PAPER runtime controller / loop shell.

OFFLINE ONLY. This module composes an already-assembled
``PaperRuntimeAssembly`` with a local config and state layout and exposes the
explicit lifecycle used by the future PAPER path:

    construct -> preflight -> connect -> bootstrap -> mark trader ready
              -> poll/run -> shutdown/disconnect

Hard boundaries preserved here:

- ``construct != connect``: constructing this controller (or importing the
  module) performs zero network/provider/credential/account/order action. It
  only wires the injected assembly.
- ``preflight != connect``: ``preflight()`` is read-only and never reaches a
  broker/account.
- ``observe != submit``: the loop only feeds closed 1m bars through the
  existing ``PaperLiveOneMinuteTransport -> PaperRuntimeCoordinator`` path;
  order submission is reached only through the coordinator's existing
  authority/risk gates.

The controller does not implement trading logic and does not add scheduling,
HA, service-cluster or multi-broker infrastructure. Graceful stop is supported
through an injected stop predicate and a bounded poll loop.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from src.paper_live_transport import TransportPollResult
from src.paper_preflight import (
    EXTERNAL,
    PaperPreflightReport,
    run_paper_preflight,
)
from src.paper_runtime_assembly import PaperRuntimeAssembly
from src.paper_runtime_config import PaperRuntimeConfig
from src.paper_runtime_layout import PaperRuntimeLayout
from src.paper_supervisor import PaperSupervisorAssessment

PAPER_RUNTIME_CONTROLLER_VERSION = "KPE_PAPER_RUNTIME_CONTROLLER_V0_1"


def _aware(value: datetime, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


@dataclass(frozen=True)
class PaperLoopStats:
    polls: int
    deliveries: int
    wake_results: int

    @property
    def identity(self) -> str:
        from hashlib import sha256
        import json
        return sha256(json.dumps({
            "controller_version": PAPER_RUNTIME_CONTROLLER_VERSION,
            "polls": self.polls,
            "deliveries": self.deliveries,
            "wake_results": self.wake_results,
        }, sort_keys=True).encode("utf-8")).hexdigest()


class PaperRuntimeController:
    """Local single-owner PAPER startup/lifecycle shell.

    Construction wires the injected assembly with the local config/layout and
    performs no external action. Every consequential method delegates to the
    existing ``PaperRuntimeCoordinator`` / ``PaperLiveOneMinuteTransport``,
    which already enforce the PAPER authority, activation-profile and risk
    gates.
    """

    def __init__(
        self,
        *,
        config: PaperRuntimeConfig,
        layout: PaperRuntimeLayout,
        assembly: PaperRuntimeAssembly,
    ) -> None:
        if not isinstance(config, PaperRuntimeConfig):
            raise TypeError("paper runtime controller requires PaperRuntimeConfig")
        if not isinstance(layout, PaperRuntimeLayout):
            raise TypeError("paper runtime controller requires PaperRuntimeLayout")
        if not isinstance(assembly, PaperRuntimeAssembly):
            raise TypeError("paper runtime controller requires PaperRuntimeAssembly")
        if assembly.trader_identity != config.trader_identity:
            raise ValueError("PAPER_CONTROLLER_TRADER_IDENTITY_MISMATCH")
        if assembly.concrete_contract_id != config.concrete_contract_id:
            raise ValueError("PAPER_CONTROLLER_CONTRACT_IDENTITY_MISMATCH")
        if assembly.coordinator.order_journal.path != layout.order_journal_path:
            raise ValueError("PAPER_CONTROLLER_ORDER_JOURNAL_PATH_MISMATCH")
        if assembly.coordinator.wake_journal.path != layout.wake_journal_path:
            raise ValueError("PAPER_CONTROLLER_WAKE_JOURNAL_PATH_MISMATCH")
        self.config = config
        self.layout = layout
        self.assembly = assembly
        self._closed = False

    # ------------------------------------------------------------------ state

    @property
    def coordinator(self):
        return self.assembly.coordinator

    @property
    def transport(self):
        return self.assembly.transport

    @property
    def supervisor(self):
        return self.assembly.supervisor

    @property
    def closed(self) -> bool:
        return self._closed

    # ------------------------------------------------------------- preflight

    def preflight(self, *, mode: str = EXTERNAL) -> PaperPreflightReport:
        """Read-only PAPER startup preflight (never reaches broker/account)."""
        if self._closed:
            raise RuntimeError("PAPER_CONTROLLER_CLOSED")
        return run_paper_preflight(
            config=self.config,
            layout=self.layout,
            activation_profile=self.config.activation_profile,
            authority=self.config.authority,
            assembly=self.assembly,
            mode=mode,
        )

    # --------------------------------------------------------------- connect

    def connect(self, *, at: datetime) -> PaperSupervisorAssessment:
        """Authority -> broker connect -> complete broker truth/reconciliation.

        Delegates to ``PaperRuntimeCoordinator.connect``, which enforces the
        PAPER connect authority gate. No-op after the controller is closed.
        """
        _aware(at, "paper controller connect time")
        if self._closed:
            raise RuntimeError("PAPER_CONTROLLER_CLOSED")
        return self.coordinator.connect(at=at)

    def disconnect(self, *, at: datetime) -> None:
        """Safe disconnect (never adds risk)."""
        _aware(at, "paper controller disconnect time")
        self.coordinator.disconnect(at=at)

    # -------------------------------------------------------------- bootstrap

    def bootstrap(self, *, observed_at: datetime):
        """Bootstrap the live 1m transport / causal context after broker truth."""
        _aware(observed_at, "paper controller bootstrap time")
        if self._closed:
            raise RuntimeError("PAPER_CONTROLLER_CLOSED")
        return self.transport.bootstrap(observed_at=observed_at)

    def mark_trader_ready(self, ready: bool = True) -> None:
        """Explicitly mark the trader runtime ready (observe eligibility)."""
        if self._closed:
            raise RuntimeError("PAPER_CONTROLLER_CLOSED")
        self.coordinator.mark_trader_runtime_ready(ready)

    # -------------------------------------------------------------- observe

    def poll(self, *, observed_at: datetime) -> TransportPollResult:
        """Drive newly closed 1m bars into the coordinator (observe, not submit).

        Submission is only ever reached through the coordinator's existing
        authority/risk gates if a decision + deterministic risk plan authorizes
        it.
        """
        _aware(observed_at, "paper controller poll time")
        if self._closed:
            raise RuntimeError("PAPER_CONTROLLER_CLOSED")
        return self.transport.poll(observed_at=observed_at)

    def run_loop(
        self,
        *,
        observed_at_provider: Callable[[], datetime],
        should_stop: Callable[[], bool] | None = None,
        max_polls: int | None = None,
    ) -> PaperLoopStats:
        """Graceful bounded poll loop around the existing transport path.

        ``should_stop`` (a predicate) or ``max_polls`` bounds the loop; either
        may be used alone or together. No scheduling/HA infrastructure is
        introduced.
        """
        if not callable(observed_at_provider):
            raise TypeError("paper loop requires an observed_at provider callable")
        if should_stop is not None and not callable(should_stop):
            raise TypeError("paper loop should_stop must be callable or None")
        if max_polls is not None and (type(max_polls) is not int or max_polls < 0):
            raise ValueError("paper loop max_polls must be a non-negative integer")
        polls = 0
        deliveries = 0
        wake_results = 0
        while True:
            if self._closed:
                break
            if should_stop is not None and should_stop():
                break
            if max_polls is not None and polls >= max_polls:
                break
            observed_at = _aware(observed_at_provider(), "paper loop observed_at")
            result = self.poll(observed_at=observed_at)
            polls += 1
            if result.bars:
                deliveries += 1
            consumer_result = result.consumer_result
            if consumer_result is not None:
                try:
                    wake_results += len(tuple(consumer_result))
                except TypeError:
                    wake_results += 1
        return PaperLoopStats(polls=polls, deliveries=deliveries, wake_results=wake_results)

    # -------------------------------------------------------------- shutdown

    def shutdown(self, *, at: datetime, persist_checkpoint: bool = True) -> None:
        """Graceful shutdown: disconnect, persist causal checkpoint, close.

        ``persist_checkpoint`` writes the causal-context snapshot to the layout
        so a restart can reopen deterministic durable state instead of wiping
        it. Journal handles are closed through the coordinator. The controller
        is permanently closed afterward.
        """
        _aware(at, "paper controller shutdown time")
        if self._closed:
            return
        try:
            self.coordinator.disconnect(at=at)
        finally:
            if persist_checkpoint:
                try:
                    snapshot = self.assembly.context_builder.snapshot()
                    self.layout.write_causal_checkpoint(snapshot)
                except Exception:  # noqa: BLE001 - shutdown must still close
                    pass
            try:
                self.coordinator.order_journal.close()
            except Exception:  # noqa: BLE001
                pass
            try:
                self.coordinator.wake_journal.close()
            except Exception:  # noqa: BLE001
                pass
            self._closed = True


__all__ = [
    "PAPER_RUNTIME_CONTROLLER_VERSION",
    "PaperLoopStats",
    "PaperRuntimeController",
]

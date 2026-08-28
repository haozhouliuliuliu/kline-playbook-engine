"""TqSdk PAPER candidate behind the project-owned BrokerAdapter surface.

No TqSdk import, network connection, account login or credential read occurs by
importing this module. The adapter wraps an injected driver so all project logic
remains broker-neutral. A future TqSdk driver may use TqSim/TqKq, but only after
separate tool verification/adoption and exact PAPER authority.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Protocol

from src.broker_adapter import (
    BrokerAccountSnapshot,
    BrokerAdapter,
    BrokerOrderInstruction,
    BrokerOrderSnapshot,
    BrokerPositionSnapshot,
)
from src.paper_execution_authority import PaperExecutionAuthority
from src.paper_order_journal import PaperOrderJournal
from src.runtime_events import BrokerConnectionState, BrokerEvent


TQSDK_PAPER_CANDIDATE_VERSION = "KPE_TQSDK_PAPER_CANDIDATE_V0_1"


class TqSdkPaperDriver(Protocol):
    """Injected third-party driver seam.

    Implementations own all TqSdk object translation. They must return only
    project-owned generic snapshots/events to the adapter.
    """

    @property
    def broker_id(self) -> str: ...

    @property
    def connection_state(self) -> BrokerConnectionState: ...

    def connect(self) -> None: ...
    def disconnect(self) -> None: ...
    def submit_order(self, instruction: BrokerOrderInstruction) -> str: ...
    def cancel_order(self, order_id: str) -> None: ...
    def replace_order(self, order_id: str, new_quantity: Decimal) -> None: ...
    def drain_events(self) -> tuple[BrokerEvent, ...]: ...
    def fetch_account_snapshot(self) -> BrokerAccountSnapshot: ...
    def fetch_position_snapshot(self) -> tuple[BrokerPositionSnapshot, ...]: ...
    def fetch_order_snapshot(self) -> tuple[BrokerOrderSnapshot, ...]: ...
    def capture_snapshot(self) -> Any: ...
    def restore_snapshot(self, snapshot: Any) -> None: ...


class TqSdkPaperBrokerAdapter(BrokerAdapter):
    """Authority-gated adapter candidate for future TqSdk PAPER execution.

    Connection, submission, cancellation and replacement are separately gated.
    This prevents a future model/runtime path from reaching an injected TqSdk
    driver merely because credentials happen to exist on the workstation.

    A pure adapter may be constructed around a non-journal test driver to verify
    authority gating. Admission to ``PaperRuntimeCoordinator`` is stricter: only
    a driver that exposes the exact project ``PaperOrderJournal`` reports
    ``journal_managed_execution=True`` and can enter the runtime composition.
    """

    def __init__(self, driver: TqSdkPaperDriver, authority: PaperExecutionAuthority) -> None:
        if not getattr(driver, "broker_id", ""):
            raise ValueError("TqSdk paper driver requires a broker identity")
        if not isinstance(authority, PaperExecutionAuthority):
            raise ValueError("TqSdk paper adapter requires PaperExecutionAuthority")
        journal = getattr(driver, "order_journal", None)
        if journal is None:
            # Current project-owned driver stores the explicit constructor-bound
            # journal privately; pure test doubles may intentionally have none.
            journal = getattr(driver, "_journal", None)
        self._driver = driver
        self._authority = authority
        driver_authority = getattr(driver, "authority", None)
        if driver_authority is not None and driver_authority is not authority:
            raise ValueError("TQSDK_PAPER_DRIVER_AUTHORITY_MISMATCH")
        self._order_journal = journal if isinstance(journal, PaperOrderJournal) else None

    @property
    def authority(self) -> PaperExecutionAuthority:
        return self._authority

    @property
    def broker_id(self) -> str:
        return self._driver.broker_id

    @property
    def journal_managed_execution(self) -> bool:
        return isinstance(self._order_journal, PaperOrderJournal)

    @property
    def order_journal(self) -> PaperOrderJournal | None:
        return self._order_journal

    @property
    def connection_state(self) -> BrokerConnectionState:
        return self._driver.connection_state

    @property
    def account_identity(self) -> str | None:
        return getattr(self._driver, "account_identity", None)

    @property
    def session_owner(self) -> object:
        return self._driver

    @property
    def runtime_version(self) -> str:
        return getattr(self._driver, "runtime_version", "UNVERIFIED")

    @property
    def identity_id(self) -> str:
        return getattr(self._driver, "identity_id", TQSDK_PAPER_CANDIDATE_VERSION)

    @property
    def execution_price_policy(self):
        return getattr(self._driver, "execution_price_policy", None)

    @property
    def close_offset_policy(self):
        return getattr(self._driver, "close_offset_policy", None)

    def connect(self) -> None:
        self._authority.require_connect()
        self._driver.connect()

    def disconnect(self) -> None:
        # Disconnect is always allowed as a safety action; it cannot add risk.
        self._driver.disconnect()

    def submit_order(self, instruction: BrokerOrderInstruction) -> str:
        if not isinstance(instruction, BrokerOrderInstruction):
            raise ValueError("submit_order requires BrokerOrderInstruction")
        self._authority.require_order_submit(instruction.concrete_contract_id)
        if self.connection_state is not BrokerConnectionState.CONNECTED:
            raise RuntimeError("PAPER_BROKER_NOT_CONNECTED")
        return self._driver.submit_order(instruction)

    def cancel_order(self, order_id: str) -> None:
        if not isinstance(order_id, str) or not order_id.strip():
            raise ValueError("cancel_order requires order id")
        self._authority.require_order_cancel()
        if self.connection_state is not BrokerConnectionState.CONNECTED:
            raise RuntimeError("PAPER_BROKER_NOT_CONNECTED")
        self._driver.cancel_order(order_id)

    def replace_order(self, order_id: str, new_quantity: Decimal) -> None:
        """Keep third-party atomic replacement behind the existing fail-closed seam.

        The active project runtime never calls this method. Safe replacement is
        owned by PaperRuntimeCoordinator as durable cancel -> exact broker truth
        -> one child submit, so UNKNOWN cancel state cannot be bypassed.
        """
        if not isinstance(order_id, str) or not order_id.strip():
            raise ValueError("replace_order requires order id")
        if type(new_quantity) is not Decimal or not new_quantity.is_finite() or new_quantity <= 0:
            raise ValueError("replace quantity must be a positive finite Decimal")
        self._authority.require_order_replace()
        if self.connection_state is not BrokerConnectionState.CONNECTED:
            raise RuntimeError("PAPER_BROKER_NOT_CONNECTED")
        self._driver.replace_order(order_id, new_quantity)

    def drain_events(self) -> tuple[BrokerEvent, ...]:
        return self._driver.drain_events()

    def pump_events(self) -> tuple[BrokerEvent, ...]:
        poll = getattr(self._driver, "poll", None)
        if not callable(poll):
            raise RuntimeError("TQSDK_DRIVER_EVENT_PUMP_MISSING")
        poll()
        return self._driver.drain_events()

    def fetch_account_snapshot(self) -> BrokerAccountSnapshot:
        return self._driver.fetch_account_snapshot()

    def fetch_position_snapshot(self) -> tuple[BrokerPositionSnapshot, ...]:
        return self._driver.fetch_position_snapshot()

    def fetch_order_snapshot(self) -> tuple[BrokerOrderSnapshot, ...]:
        return self._driver.fetch_order_snapshot()

    def capture_snapshot(self) -> Any:
        return self._driver.capture_snapshot()

    def restore_snapshot(self, snapshot: Any) -> None:
        self._driver.restore_snapshot(snapshot)

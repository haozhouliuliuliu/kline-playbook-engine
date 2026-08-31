"""Deterministic offline CTP transport for lifecycle and failure drills.

The fake imports no vendor SDK, reads no credentials, opens no connection and
uses no wall clock.  Callers provide an exact operation script and exact
callbacks.  Any unexpected operation fails immediately.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.fangzheng_ctp_candidate import (
    CtpCallback,
    CtpCancelRequest,
    CtpSubmitRequest,
)


class FakeCtpOperation(str, Enum):
    CONNECT = "CONNECT"
    DISCONNECT = "DISCONNECT"
    AUTHENTICATE = "AUTHENTICATE"
    LOGIN = "LOGIN"
    SUBMIT = "SUBMIT"
    CANCEL = "CANCEL"
    QUERY_ACCOUNT = "QUERY_ACCOUNT"
    QUERY_POSITIONS = "QUERY_POSITIONS"
    QUERY_ORDERS = "QUERY_ORDERS"
    QUERY_TRADES = "QUERY_TRADES"


@dataclass(frozen=True)
class FakeCtpStep:
    operation: FakeCtpOperation
    callbacks: tuple[CtpCallback, ...] = ()
    expected_project_order_id: str | None = None
    failure_after_effect: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.operation, FakeCtpOperation):
            raise ValueError("fake CTP step requires an explicit operation")
        if not isinstance(self.callbacks, tuple) or any(
            not isinstance(item, CtpCallback) for item in self.callbacks
        ):
            raise ValueError("fake CTP callbacks must be a tuple of CtpCallback values")
        if self.expected_project_order_id is not None and (
            not isinstance(self.expected_project_order_id, str)
            or not self.expected_project_order_id.strip()
        ):
            raise ValueError("fake CTP expected project order id must be non-empty")
        if self.failure_after_effect is not None and (
            not isinstance(self.failure_after_effect, str)
            or not self.failure_after_effect.strip()
        ):
            raise ValueError("fake CTP failure must be a non-empty string")


class ScriptedCtpTransport:
    """Strict in-memory ``CtpTransport`` implementation.

    Each transport call consumes exactly one scripted step.  Callbacks become
    visible only through ``drain_callbacks``.  ``failure_after_effect`` models
    an exception after the request crossed the project/transport seam.
    """

    def __init__(
        self,
        steps: tuple[FakeCtpStep, ...],
        *,
        broker_id: str = "fangzheng-ctp-offline-scripted-fake",
    ) -> None:
        if not isinstance(steps, tuple) or any(not isinstance(item, FakeCtpStep) for item in steps):
            raise ValueError("fake CTP script must be a tuple of FakeCtpStep values")
        if not isinstance(broker_id, str) or not broker_id.strip():
            raise ValueError("fake CTP broker id must be non-empty")
        self._broker_id = broker_id
        self._remaining = list(steps)
        self._callbacks: list[CtpCallback] = []
        self._operations: list[FakeCtpOperation] = []
        self._submits: list[CtpSubmitRequest] = []
        self._cancels: list[CtpCancelRequest] = []

    @property
    def broker_id(self) -> str:
        return self._broker_id

    @property
    def operations(self) -> tuple[FakeCtpOperation, ...]:
        return tuple(self._operations)

    @property
    def submits(self) -> tuple[CtpSubmitRequest, ...]:
        return tuple(self._submits)

    @property
    def cancels(self) -> tuple[CtpCancelRequest, ...]:
        return tuple(self._cancels)

    def inject_callbacks(self, callbacks: tuple[CtpCallback, ...]) -> None:
        if not isinstance(callbacks, tuple) or any(
            not isinstance(item, CtpCallback) for item in callbacks
        ):
            raise ValueError("injected callbacks must be a tuple of CtpCallback values")
        self._callbacks.extend(callbacks)

    def assert_exhausted(self) -> None:
        if self._remaining:
            operations = ",".join(item.operation.value for item in self._remaining)
            raise AssertionError(f"FAKE_CTP_SCRIPT_NOT_EXHAUSTED:{operations}")
        if self._callbacks:
            raise AssertionError("FAKE_CTP_CALLBACKS_NOT_DRAINED")

    def connect(self) -> None:
        self._consume(FakeCtpOperation.CONNECT)

    def disconnect(self) -> None:
        self._consume(FakeCtpOperation.DISCONNECT)

    def authenticate(self) -> None:
        self._consume(FakeCtpOperation.AUTHENTICATE)

    def login(self) -> None:
        self._consume(FakeCtpOperation.LOGIN)

    def submit_order(self, request: CtpSubmitRequest) -> None:
        if not isinstance(request, CtpSubmitRequest):
            raise ValueError("fake CTP submit requires CtpSubmitRequest")
        self._consume(
            FakeCtpOperation.SUBMIT,
            request.project_order_id,
            submit_request=request,
        )

    def cancel_order(self, request: CtpCancelRequest) -> None:
        if not isinstance(request, CtpCancelRequest):
            raise ValueError("fake CTP cancel requires CtpCancelRequest")
        self._consume(
            FakeCtpOperation.CANCEL,
            request.project_order_id,
            cancel_request=request,
        )

    def request_account(self) -> None:
        self._consume(FakeCtpOperation.QUERY_ACCOUNT)

    def request_positions(self) -> None:
        self._consume(FakeCtpOperation.QUERY_POSITIONS)

    def request_orders(self) -> None:
        self._consume(FakeCtpOperation.QUERY_ORDERS)

    def request_trades(self) -> None:
        self._consume(FakeCtpOperation.QUERY_TRADES)

    def drain_callbacks(self) -> tuple[CtpCallback, ...]:
        callbacks = tuple(self._callbacks)
        self._callbacks.clear()
        return callbacks

    def _consume(
        self,
        operation: FakeCtpOperation,
        project_order_id: str | None = None,
        *,
        submit_request: CtpSubmitRequest | None = None,
        cancel_request: CtpCancelRequest | None = None,
    ) -> None:
        if not self._remaining:
            raise RuntimeError(f"UNSCRIPTED_FAKE_CTP_OPERATION:{operation.value}")
        step = self._remaining.pop(0)
        if step.operation is not operation:
            raise RuntimeError(
                f"FAKE_CTP_OPERATION_MISMATCH:expected={step.operation.value}:actual={operation.value}"
            )
        if (
            step.expected_project_order_id is not None
            and step.expected_project_order_id != project_order_id
        ):
            raise RuntimeError("FAKE_CTP_PROJECT_ORDER_ID_MISMATCH")
        self._operations.append(operation)
        if submit_request is not None:
            self._submits.append(submit_request)
        if cancel_request is not None:
            self._cancels.append(cancel_request)
        self._callbacks.extend(step.callbacks)
        if step.failure_after_effect is not None:
            raise RuntimeError(step.failure_after_effect)

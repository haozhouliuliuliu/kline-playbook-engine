"""Thin TqSdk-like live 1m source behind the project transport protocol."""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
from typing import Callable, Mapping, Protocol, Sequence


class TqSdkLiveDataSession(Protocol):
    def read_recent_1m_rows(
        self, *, symbol: str, limit: int
    ) -> Sequence[Mapping[str, object]]: ...

    def authoritative_update_at(self) -> datetime | None: ...


class TqSdkLiveOneMinuteSource:
    """Bind one exact full contract to an already-authorized shared session.

    Construction is pure.  The session provider is invoked only by runtime
    readiness/read calls after the controller has connected the broker.
    """

    def __init__(
        self,
        *,
        concrete_contract_id: str,
        session_provider: Callable[[], TqSdkLiveDataSession],
    ) -> None:
        if not isinstance(concrete_contract_id, str) or "." not in concrete_contract_id:
            raise ValueError("TqSdk live source requires a full concrete contract")
        if not callable(session_provider):
            raise TypeError("TqSdk live source requires a session provider")
        self._contract = concrete_contract_id
        self._session_provider = session_provider
        self._session_owner = getattr(session_provider, "__self__", None)

    @property
    def contract_identity(self) -> str:
        return self._contract

    @property
    def session_owner(self) -> object | None:
        return self._session_owner

    @property
    def identity_id(self) -> str:
        return sha256(json.dumps({
            "kind": "TQSDK_LIVE_ONE_MINUTE_SOURCE_V0_1",
            "contract": self._contract,
            "duration_seconds": 60,
        }, sort_keys=True).encode("utf-8")).hexdigest()

    @property
    def connected(self) -> bool:
        try:
            self._session_provider()
        except RuntimeError:
            return False
        return True

    def last_activity_at(self) -> datetime | None:
        return self._session_provider().authoritative_update_at()

    def read_recent_1m_rows(
        self, *, symbol: str, limit: int
    ) -> tuple[Mapping[str, object], ...]:
        if symbol != self._contract:
            raise ValueError("TQSDK_LIVE_SOURCE_CONTRACT_MISMATCH")
        if type(limit) is not int or limit <= 0:
            raise ValueError("TqSdk live source limit must be positive")
        rows = self._session_provider().read_recent_1m_rows(
            symbol=symbol, limit=limit
        )
        if not isinstance(rows, Sequence):
            raise RuntimeError("TQSDK_LIVE_SOURCE_ROWS_NOT_SEQUENCE")
        return tuple(rows)


__all__ = ["TqSdkLiveDataSession", "TqSdkLiveOneMinuteSource"]

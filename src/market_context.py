"""Deterministic causal MarketContext for historical, shadow and live PAPER use.

MarketContext consumes only completed evidence. Historical normalized bars and
future broker-neutral live closed bars share this surface without pretending
that live data is a historical artifact.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from hashlib import sha256
import json
from typing import Any

from src.contract_semantics import ContractSpecification
from src.data_substrate import CompletedBar

MARKET_CONTEXT_SCHEMA_VERSION = "shadow-runtime-market-context-v0.2"

def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()

def _completed_bar_of(value: Any) -> CompletedBar:
    if isinstance(value, CompletedBar):
        return value
    completed = getattr(value, "completed_bar", None)
    if isinstance(completed, CompletedBar):
        return completed
    raise ValueError("market context requires a CompletedBar-backed evidence object")

@dataclass(frozen=True)
class MarketContext:
    """One completed-bar causal context snapshot for intent computation."""

    instrument: str
    concrete_contract_id: str
    last_completed_bar: Any
    observed_at: datetime
    staleness_threshold: timedelta | None
    contract_spec: ContractSpecification | None = None
    session_metadata_version: str | None = None
    feature_identities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.instrument or not self.concrete_contract_id:
            raise ValueError("market context requires instrument and concrete contract identities")
        _completed_bar_of(self.last_completed_bar)
        if self.observed_at.tzinfo is None:
            raise ValueError("market context observation timestamp must be timezone-aware")
        if self.staleness_threshold is not None and self.staleness_threshold < timedelta(0):
            raise ValueError("market context staleness threshold cannot be negative")
        if self.contract_spec is not None and self.contract_spec.instrument_id != self.concrete_contract_id:
            raise ValueError("market context contract spec disagrees with the concrete contract")
        if not isinstance(self.feature_identities, tuple):
            raise ValueError("market context feature identities must be a tuple")

    @property
    def completed_bar(self) -> CompletedBar:
        return _completed_bar_of(self.last_completed_bar)

    @property
    def available_at(self) -> datetime:
        return self.completed_bar.available_at

    @property
    def trading_day(self) -> date:
        return self.completed_bar.trading_day

    def latest_price(self) -> Decimal:
        close = getattr(self.last_completed_bar, "close", None)
        if type(close) is not Decimal or not close.is_finite() or close <= 0:
            raise ValueError("market context price evidence requires a positive finite Decimal close")
        return close

    def is_stale(self, now: datetime) -> bool:
        if now.tzinfo is None:
            raise ValueError("staleness check requires a timezone-aware timestamp")
        if self.staleness_threshold is None:
            return False
        return now - self.available_at > self.staleness_threshold

    @property
    def bar_identity(self) -> str:
        return self.completed_bar.start.isoformat()

    @property
    def identity_id(self) -> str:
        evidence_identity = getattr(self.last_completed_bar, "identity_id", None)
        return _canonical_hash({
            "schema_version": MARKET_CONTEXT_SCHEMA_VERSION,
            "instrument": self.instrument,
            "concrete_contract_id": self.concrete_contract_id,
            "bar_start": self.completed_bar.start.isoformat(),
            "bar_end": self.completed_bar.end.isoformat(),
            "bar_available_at": self.completed_bar.available_at.isoformat(),
            "bar_quality_partial": self.completed_bar.quality.partial,
            "bar_quality_reconnect_gap": self.completed_bar.quality.reconnect_gap,
            "observed_at": self.observed_at.isoformat(),
            "staleness_threshold": None if self.staleness_threshold is None else int(self.staleness_threshold.total_seconds()),
            "contract_spec_identity": None if self.contract_spec is None else self.contract_spec.identity_id,
            "session_metadata_version": self.session_metadata_version,
            "feature_identities": self.feature_identities,
            "evidence_identity": evidence_identity,
        })

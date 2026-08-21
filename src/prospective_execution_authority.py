"""Point-in-time prospective execution facts; missing facts always deny.

This module intentionally does not provide historical backfill.  It is a small
seam for a future authorised Shadow collector to inject source-bound facts that
were available before a decision.  It contains no network, broker, price, or
candidate-outcome access.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
import json
from typing import Iterable


def _hash(value: object) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")


class ProspectiveExecutionAuthorityError(ValueError):
    """A source fact required for a future Shadow decision is absent or invalid."""


@dataclass(frozen=True)
class ProspectiveFeeMarginFact:
    concrete_contract_id: str
    effective_at: datetime
    available_at: datetime
    source_identity: str
    fee_per_round_trip: Decimal
    initial_margin_rate: Decimal

    def __post_init__(self) -> None:
        _text(self.concrete_contract_id, "concrete contract")
        _text(self.source_identity, "fee/margin source identity")
        if self.effective_at.tzinfo is None or self.available_at.tzinfo is None:
            raise ValueError("fee/margin timestamps must be timezone-aware")
        if self.available_at > self.effective_at:
            raise ValueError("fee/margin fact must be available no later than effective_at")
        if any(type(value) is not Decimal or not value.is_finite() or value < 0 for value in (self.fee_per_round_trip, self.initial_margin_rate)):
            raise ValueError("fee/margin values must be non-negative finite Decimals")

    @property
    def identity_id(self) -> str:
        return _hash({"contract": self.concrete_contract_id, "effective_at": self.effective_at.isoformat(), "available_at": self.available_at.isoformat(), "source": self.source_identity, "fee": str(self.fee_per_round_trip), "margin": str(self.initial_margin_rate)})


@dataclass(frozen=True)
class ProspectivePriceLimitFact:
    concrete_contract_id: str
    trading_day: date
    effective_at: datetime
    available_at: datetime
    source_identity: str
    lower_limit: Decimal
    upper_limit: Decimal

    def __post_init__(self) -> None:
        _text(self.concrete_contract_id, "concrete contract")
        _text(self.source_identity, "price-limit source identity")
        if self.effective_at.tzinfo is None or self.available_at.tzinfo is None:
            raise ValueError("price-limit timestamps must be timezone-aware")
        if self.available_at > self.effective_at or self.effective_at.date() != self.trading_day:
            raise ValueError("price-limit fact chronology is invalid")
        if type(self.lower_limit) is not Decimal or type(self.upper_limit) is not Decimal or not self.lower_limit.is_finite() or not self.upper_limit.is_finite() or self.lower_limit <= 0 or self.upper_limit <= self.lower_limit:
            raise ValueError("price-limit bounds must be positive ordered finite Decimals")

    @property
    def identity_id(self) -> str:
        return _hash({"contract": self.concrete_contract_id, "day": self.trading_day.isoformat(), "effective_at": self.effective_at.isoformat(), "available_at": self.available_at.isoformat(), "source": self.source_identity, "lower": str(self.lower_limit), "upper": str(self.upper_limit)})


@dataclass(frozen=True)
class ProspectiveSlippageAuthority:
    """An explicit source-bound slippage policy; zero is never an implicit default."""

    authority_identity: str
    configured: bool
    model_reference: str | None = None

    def __post_init__(self) -> None:
        _text(self.authority_identity, "slippage authority identity")
        if self.configured and (not isinstance(self.model_reference, str) or not self.model_reference.strip()):
            raise ValueError("configured slippage authority requires a model reference")
        if not self.configured and self.model_reference is not None:
            raise ValueError("unconfigured slippage authority cannot name a model")


class ProspectiveExecutionAuthority:
    """Deep module for retrieving only PIT-valid future execution facts."""

    def __init__(self, *, fee_margin_facts: Iterable[ProspectiveFeeMarginFact] = (), price_limit_facts: Iterable[ProspectivePriceLimitFact] = (), slippage_authority: ProspectiveSlippageAuthority | None = None) -> None:
        self._fees = tuple(fee_margin_facts)
        self._limits = tuple(price_limit_facts)
        self._slippage = slippage_authority or ProspectiveSlippageAuthority("SLIPPAGE_AUTHORITY_UNCONFIGURED", False)
        if len({item.identity_id for item in self._fees}) != len(self._fees) or len({item.identity_id for item in self._limits}) != len(self._limits):
            raise ValueError("prospective execution facts must be unique")

    @property
    def identity_id(self) -> str:
        return _hash({"fees": sorted(item.identity_id for item in self._fees), "limits": sorted(item.identity_id for item in self._limits), "slippage": self._slippage.authority_identity, "slippage_configured": self._slippage.configured})

    def require_fee_margin(self, concrete_contract_id: str, decision_at: datetime) -> ProspectiveFeeMarginFact:
        candidates = [item for item in self._fees if item.concrete_contract_id == concrete_contract_id and item.available_at <= decision_at and item.effective_at <= decision_at]
        if not candidates:
            raise ProspectiveExecutionAuthorityError("PROSPECTIVE_FEE_MARGIN_FACT_MISSING_OR_AMBIGUOUS")
        latest = max(candidates, key=lambda item: item.effective_at)
        if sum(item.effective_at == latest.effective_at for item in candidates) != 1:
            raise ProspectiveExecutionAuthorityError("PROSPECTIVE_FEE_MARGIN_FACT_MISSING_OR_AMBIGUOUS")
        return latest

    def require_price_limit(self, concrete_contract_id: str, trading_day: date, decision_at: datetime) -> ProspectivePriceLimitFact:
        candidates = [item for item in self._limits if item.concrete_contract_id == concrete_contract_id and item.trading_day == trading_day and item.available_at <= decision_at and item.effective_at <= decision_at]
        if len(candidates) != 1:
            raise ProspectiveExecutionAuthorityError("PROSPECTIVE_PRICE_LIMIT_FACT_MISSING_OR_AMBIGUOUS")
        return candidates[0]

    def require_slippage(self) -> ProspectiveSlippageAuthority:
        if not self._slippage.configured:
            raise ProspectiveExecutionAuthorityError("PROSPECTIVE_SLIPPAGE_AUTHORITY_UNCONFIGURED")
        return self._slippage

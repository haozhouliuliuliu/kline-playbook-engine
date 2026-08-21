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
    version: str = "v1"
    product_scope: str | None = None
    provenance: str | None = None
    source_bytes_sha256: str | None = None

    def __post_init__(self) -> None:
        _text(self.concrete_contract_id, "concrete contract")
        _text(self.source_identity, "fee/margin source identity")
        _text(self.version, "fee/margin version")
        if self.effective_at.tzinfo is None or self.available_at.tzinfo is None:
            raise ValueError("fee/margin timestamps must be timezone-aware")
        if self.available_at > self.effective_at:
            raise ValueError("fee/margin fact must be available no later than effective_at")
        if any(type(value) is not Decimal or not value.is_finite() or value < 0 for value in (self.fee_per_round_trip, self.initial_margin_rate)):
            raise ValueError("fee/margin values must be non-negative finite Decimals")

    @property
    def identity_id(self) -> str:
        return _hash({"contract": self.concrete_contract_id, "effective_at": self.effective_at.isoformat(), "available_at": self.available_at.isoformat(), "source": self.source_identity, "fee": str(self.fee_per_round_trip), "margin": str(self.initial_margin_rate), "version": self.version, "scope": self.product_scope, "provenance": self.provenance, "source_bytes_sha256": self.source_bytes_sha256})


@dataclass(frozen=True)
class ProspectivePriceLimitFact:
    concrete_contract_id: str
    trading_day: date
    effective_at: datetime
    available_at: datetime
    source_identity: str
    lower_limit: Decimal
    upper_limit: Decimal
    version: str = "v1"
    product_scope: str | None = None
    provenance: str | None = None
    source_bytes_sha256: str | None = None

    def __post_init__(self) -> None:
        _text(self.concrete_contract_id, "concrete contract")
        _text(self.source_identity, "price-limit source identity")
        _text(self.version, "price-limit version")
        if self.effective_at.tzinfo is None or self.available_at.tzinfo is None:
            raise ValueError("price-limit timestamps must be timezone-aware")
        if self.available_at > self.effective_at or self.effective_at.date() != self.trading_day:
            raise ValueError("price-limit fact chronology is invalid")
        if type(self.lower_limit) is not Decimal or type(self.upper_limit) is not Decimal or not self.lower_limit.is_finite() or not self.upper_limit.is_finite() or self.lower_limit <= 0 or self.upper_limit <= self.lower_limit:
            raise ValueError("price-limit bounds must be positive ordered finite Decimals")

    @property
    def identity_id(self) -> str:
        return _hash({"contract": self.concrete_contract_id, "day": self.trading_day.isoformat(), "effective_at": self.effective_at.isoformat(), "available_at": self.available_at.isoformat(), "source": self.source_identity, "lower": str(self.lower_limit), "upper": str(self.upper_limit), "version": self.version, "scope": self.product_scope, "provenance": self.provenance, "source_bytes_sha256": self.source_bytes_sha256})


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


@dataclass(frozen=True)
class ProspectiveSlippagePolicy:
    """Versioned, prospective-only slippage authority for a scoped contract/product."""

    policy_id: str
    scope_id: str
    version: str
    effective_at: datetime
    available_at: datetime
    source_identity: str
    provenance: str
    source_bytes_sha256: str | None
    status: str
    model_reference: str | None = None

    def __post_init__(self) -> None:
        for value, name in ((self.policy_id, "policy id"), (self.scope_id, "scope"), (self.version, "version"), (self.source_identity, "source"), (self.provenance, "provenance"), (self.status, "status")):
            _text(value, name)
        if self.effective_at.tzinfo is None or self.available_at.tzinfo is None or self.available_at > self.effective_at:
            raise ValueError("slippage policy chronology is invalid")
        if self.source_bytes_sha256 is not None and (len(self.source_bytes_sha256) != 64 or any(ch not in "0123456789abcdef" for ch in self.source_bytes_sha256)):
            raise ValueError("source bytes hash must be lowercase sha256 when provided")
        if self.status == "CONFIGURED" and not self.model_reference:
            raise ValueError("configured slippage policy requires model reference")
        if self.status not in ("CONFIGURED", "UNRESOLVED_FAIL_CLOSED", "TEST_ONLY"):
            raise ValueError("unsupported prospective slippage policy status")

    @property
    def identity_id(self) -> str:
        return _hash({"policy": self.policy_id, "scope": self.scope_id, "version": self.version, "effective": self.effective_at.isoformat(), "available": self.available_at.isoformat(), "source": self.source_identity, "provenance": self.provenance, "bytes": self.source_bytes_sha256, "status": self.status, "model": self.model_reference})


@dataclass(frozen=True)
class ProspectiveAuthorityAuditRecord:
    action: str
    fact_identity: str
    recorded_at: datetime

    @property
    def identity_id(self) -> str:
        return _hash({"action": self.action, "fact": self.fact_identity, "recorded": self.recorded_at.isoformat()})


class ProspectiveExecutionAuthorityStore:
    """Append-only local ingestion seam; lookup is always point-in-time and fail closed."""

    def __init__(self) -> None:
        self._facts: list[ProspectiveFeeMarginFact | ProspectivePriceLimitFact | ProspectiveSlippagePolicy] = []
        self._audit: list[ProspectiveAuthorityAuditRecord] = []

    @property
    def audit_log(self) -> tuple[ProspectiveAuthorityAuditRecord, ...]:
        return tuple(self._audit)

    @property
    def identity_id(self) -> str:
        return _hash({"facts": [item.identity_id for item in self._facts], "audit": [item.identity_id for item in self._audit]})

    def append(self, fact: ProspectiveFeeMarginFact | ProspectivePriceLimitFact | ProspectiveSlippagePolicy, recorded_at: datetime) -> None:
        if not isinstance(fact, (ProspectiveFeeMarginFact, ProspectivePriceLimitFact, ProspectiveSlippagePolicy)):
            raise ProspectiveExecutionAuthorityError("PROSPECTIVE_AUTHORITY_UNKNOWN_FACT_TYPE")
        if recorded_at.tzinfo is None:
            raise ValueError("authority audit timestamp must be timezone-aware")
        if fact.identity_id in {item.identity_id for item in self._facts}:
            self._audit.append(ProspectiveAuthorityAuditRecord("DUPLICATE_NOOP", fact.identity_id, recorded_at))
            return
        key = self._conflict_key(fact)
        if any(self._conflict_key(item) == key for item in self._facts):
            raise ProspectiveExecutionAuthorityError("PROSPECTIVE_AUTHORITY_CONFLICT_NO_SILENT_OVERWRITE")
        self._facts.append(fact)
        self._audit.append(ProspectiveAuthorityAuditRecord("APPEND", fact.identity_id, recorded_at))

    def authority_at(self, decision_at: datetime, *, concrete_contract_id: str, product_scope: str | None = None) -> "ProspectiveExecutionAuthority":
        if decision_at.tzinfo is None:
            raise ValueError("authority lookup requires timezone-aware decision time")
        fees = tuple(item for item in self._facts if isinstance(item, ProspectiveFeeMarginFact) and item.concrete_contract_id == concrete_contract_id)
        limits = tuple(item for item in self._facts if isinstance(item, ProspectivePriceLimitFact) and item.concrete_contract_id == concrete_contract_id)
        policies = [item for item in self._facts if isinstance(item, ProspectiveSlippagePolicy) and item.available_at <= decision_at and item.effective_at <= decision_at and item.status == "CONFIGURED" and (item.scope_id == concrete_contract_id or product_scope is not None and item.scope_id == product_scope)]
        if len(policies) > 1:
            raise ProspectiveExecutionAuthorityError("PROSPECTIVE_SLIPPAGE_POLICY_MISSING_OR_AMBIGUOUS")
        slippage = ProspectiveSlippageAuthority(policies[0].identity_id, True, policies[0].model_reference) if policies else ProspectiveSlippageAuthority("PROSPECTIVE_SLIPPAGE_POLICY_UNRESOLVED_FAIL_CLOSED", False)
        return ProspectiveExecutionAuthority(fee_margin_facts=fees, price_limit_facts=limits, slippage_authority=slippage)

    @staticmethod
    def _conflict_key(fact: ProspectiveFeeMarginFact | ProspectivePriceLimitFact | ProspectiveSlippagePolicy) -> tuple[object, ...]:
        if isinstance(fact, ProspectiveFeeMarginFact):
            return ("FEE_MARGIN", fact.concrete_contract_id, fact.effective_at)
        if isinstance(fact, ProspectivePriceLimitFact):
            return ("PRICE_LIMIT", fact.concrete_contract_id, fact.trading_day, fact.effective_at)
        return ("SLIPPAGE", fact.scope_id, fact.effective_at)


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

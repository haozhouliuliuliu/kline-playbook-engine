"""Source-aware current/future contract facts schema (additive, offline-only).

This module provides typed, deterministic containers for concrete-contract
facts (identity, exchange/product, multiplier, tick, reference price, margin,
fee/commission, price limits) that future REAL/PAPER bindings and the
capital-adequacy calculator can consume.

Design rules (fail closed):

- every fact set carries explicit provenance (source identity/type, retrieval
  timestamp, version) and freshness (``CURRENT`` / ``STALE`` / ``UNKNOWN``);
- every fact set is classified as exactly one of EXCHANGE/BROKER FACT,
  SCENARIO ASSUMPTION, JIANGHE BEHAVIOR OBSERVATION, or PERMANENT RISK POLICY
  CONSTRAINT, so callers never conflate source truth with assumptions;
- historical canonical metadata is marked ``is_historical_only`` and must
  never be labeled as current broker/account truth (a historical fact set can
  never have ``CURRENT`` freshness);
- missing money/price facts stay MISSING (``None``), never fabricated zero;
- zero commission is explicit and distinct from unknown commission;
- units are never conflated: a margin fact uses exactly one basis
  (per-lot amount OR percent of contract value), never both.

No live acquisition, no credentials, no permanent numeric risk choices, no
broker/account action. Offline engineering primitives only.  All numeric
values in tests that exercise this module are synthetic FIXTURE-ONLY values
and are never exported as production defaults.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json


def _canonical_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _canonical_decimal(value: Decimal | None) -> str | None:
    """Stable semantic Decimal text; preserves ``None`` versus explicit zero."""
    if value is None:
        return None
    normalized = value.normalize()
    text = format(normalized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if text in {"", "-0"} else text


def _margin_identity_payload(margin: "MarginFacts | None") -> object:
    if margin is None:
        return None
    return {
        "basis": margin.basis.value,
        "initial_margin_per_lot": _canonical_decimal(margin.initial_margin_per_lot),
        "maintenance_margin_per_lot": _canonical_decimal(margin.maintenance_margin_per_lot),
        "initial_margin_percent": _canonical_decimal(margin.initial_margin_percent),
        "maintenance_margin_percent": _canonical_decimal(margin.maintenance_margin_percent),
        "currency": margin.currency,
    }


def _fee_identity_payload(fee: "FeeModel | None") -> object:
    if fee is None:
        return None
    return {
        "commission_per_lot": _canonical_decimal(fee.commission_per_lot),
        "commission_percent": _canonical_decimal(fee.commission_percent),
        "currency": fee.currency,
    }


def _price_limit_identity_payload(price_limits: "PriceLimitFacts | None") -> object:
    if price_limits is None:
        return None
    return {
        "lower_price_limit": _canonical_decimal(price_limits.lower_price_limit),
        "upper_price_limit": _canonical_decimal(price_limits.upper_price_limit),
        "basis": price_limits.basis,
        "currency": price_limits.currency,
    }


def _positive_or_zero_decimal(value: object, name: str, *, allow_zero: bool) -> Decimal:
    if type(value) is not Decimal or not value.is_finite():
        raise ValueError(f"{name} must be a finite Decimal")
    if allow_zero:
        if value < 0:
            raise ValueError(f"{name} must be non-negative")
    elif value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def _required_text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")


class FactCategory(str, Enum):
    """Concern classification for a fact set (one concern, one label)."""

    EXCHANGE_BROKER_FACT = "EXCHANGE_BROKER_FACT"
    SCENARIO_ASSUMPTION = "SCENARIO_ASSUMPTION"
    JIANGHE_BEHAVIOR_OBSERVATION = "JIANGHE_BEHAVIOR_OBSERVATION"
    PERMANENT_RISK_POLICY_CONSTRAINT = "PERMANENT_RISK_POLICY_CONSTRAINT"


class FactSourceType(str, Enum):
    """Provenance type of a fact set (never implies current broker truth)."""

    EXCHANGE_OFFICIAL = "EXCHANGE_OFFICIAL"
    BROKER = "BROKER"
    HISTORICAL_CANONICAL_METADATA = "HISTORICAL_CANONICAL_METADATA"
    PROVIDER_REFERENCE = "PROVIDER_REFERENCE"
    SCENARIO_ASSUMPTION = "SCENARIO_ASSUMPTION"
    OBSERVED_BEHAVIOR = "OBSERVED_BEHAVIOR"
    UNKNOWN = "UNKNOWN"


class FactFreshness(str, Enum):
    """Freshness state of a fact set; only CURRENT is eligible for live use."""

    CURRENT = "CURRENT"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


class MarginBasis(str, Enum):
    """Exact unit basis of a margin fact (never mixed)."""

    PER_LOT_AMOUNT = "PER_LOT_AMOUNT"
    PERCENT_OF_CONTRACT_VALUE = "PERCENT_OF_CONTRACT_VALUE"


class CommissionBasis(str, Enum):
    """Exact unit basis of a commission fact (never mixed)."""

    PER_LOT_AMOUNT = "PER_LOT_AMOUNT"
    PERCENT_OF_TRADE_VALUE = "PERCENT_OF_TRADE_VALUE"


@dataclass(frozen=True)
class ContractIdentity:
    """Explicit concrete-contract identity."""

    exchange: str
    product_family: str
    instrument_id: str

    def __post_init__(self) -> None:
        for value, name in (
            (self.exchange, "contract identity exchange"),
            (self.product_family, "contract identity product family"),
            (self.instrument_id, "contract identity instrument id"),
        ):
            _required_text(value, name)

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "exchange": self.exchange,
                "product_family": self.product_family,
                "instrument_id": self.instrument_id,
            }
        )


@dataclass(frozen=True)
class SourceProvenance:
    """Explicit provenance of a fact set."""

    source_identity: str
    source_type: FactSourceType
    retrieved_at: datetime
    source_version: str
    notes: str = ""

    def __post_init__(self) -> None:
        for value, name in (
            (self.source_identity, "source provenance identity"),
            (self.source_version, "source provenance version"),
        ):
            _required_text(value, name)
        if not isinstance(self.source_type, FactSourceType):
            raise ValueError("source provenance type must be a FactSourceType")
        if self.retrieved_at.tzinfo is None:
            raise ValueError("source provenance retrieval timestamp must be timezone-aware")
        if not isinstance(self.notes, str):
            raise ValueError("source provenance notes must be a string")


@dataclass(frozen=True)
class MarginFacts:
    """Initial/maintenance margin inputs with an exact unit basis.

    ``None`` means the fact was not supplied (MISSING), never zero. A fact set
    with a supplied basis uses exactly that basis; mixing per-lot amounts and
    percents is rejected to avoid unit conflation.
    """

    basis: MarginBasis
    initial_margin_per_lot: Decimal | None = None
    maintenance_margin_per_lot: Decimal | None = None
    initial_margin_percent: Decimal | None = None
    maintenance_margin_percent: Decimal | None = None
    currency: str = "CNY"

    def __post_init__(self) -> None:
        if not isinstance(self.basis, MarginBasis):
            raise ValueError("margin basis must be a MarginBasis")
        _required_text(self.currency, "margin currency")
        per_lot = (
            self.initial_margin_per_lot,
            self.maintenance_margin_per_lot,
        )
        percent = (
            self.initial_margin_percent,
            self.maintenance_margin_percent,
        )
        for value in per_lot:
            if value is not None:
                _positive_or_zero_decimal(value, "per-lot margin", allow_zero=False)
        for value in percent:
            if value is not None:
                _positive_or_zero_decimal(value, "margin percent", allow_zero=False)
        if self.basis is MarginBasis.PER_LOT_AMOUNT:
            if any(value is not None for value in percent):
                raise ValueError("PER_LOT_AMOUNT margin facts cannot carry percent values")
        else:
            if any(value is not None for value in per_lot):
                raise ValueError("PERCENT_OF_CONTRACT_VALUE margin facts cannot carry per-lot amounts")
        if all(value is None for value in (*per_lot, *percent)):
            raise ValueError("margin facts require at least one supplied fact (None means unknown)")

    def one_lot_margin_amount(self, notional_per_lot: Decimal) -> Decimal | None:
        """Initial margin per lot in currency, or None when not derivable."""
        if self.basis is MarginBasis.PER_LOT_AMOUNT:
            if self.initial_margin_per_lot is None:
                return None
            return self.initial_margin_per_lot
        if self.initial_margin_percent is None:
            return None
        return notional_per_lot * self.initial_margin_percent / Decimal("100")


@dataclass(frozen=True)
class FeeModel:
    """Fee/commission model input.

    At least one component must be supplied.  An explicit ``0`` component is a
    real zero; a missing component (``None``) means unknown.  ``cost_for``
    returns the per-lot commission in currency for the supplied notional.
    """

    commission_per_lot: Decimal | None = None
    commission_percent: Decimal | None = None
    currency: str = "CNY"

    def __post_init__(self) -> None:
        _required_text(self.currency, "fee currency")
        for value, name in (
            (self.commission_per_lot, "commission per lot"),
            (self.commission_percent, "commission percent"),
        ):
            if value is not None:
                _positive_or_zero_decimal(value, name, allow_zero=True)
        if self.commission_per_lot is None and self.commission_percent is None:
            raise ValueError("fee model requires at least one supplied component (None means unknown)")

    def cost_for(self, notional_per_lot: Decimal) -> Decimal:
        """Per-lot commission cost in currency (explicit zero stays zero)."""
        _positive_or_zero_decimal(notional_per_lot, "fee notional", allow_zero=False)
        cost = Decimal("0")
        if self.commission_per_lot is not None:
            cost += self.commission_per_lot
        if self.commission_percent is not None:
            cost += notional_per_lot * self.commission_percent / Decimal("100")
        return cost


@dataclass(frozen=True)
class PriceLimitFacts:
    """Price-limit facts when provided (per-day operative bounds)."""

    lower_price_limit: Decimal | None
    upper_price_limit: Decimal | None
    basis: str
    currency: str

    def __post_init__(self) -> None:
        _required_text(self.basis, "price-limit basis")
        _required_text(self.currency, "price-limit currency")
        for value, name in (
            (self.lower_price_limit, "lower price limit"),
            (self.upper_price_limit, "upper price limit"),
        ):
            if value is not None:
                _positive_or_zero_decimal(value, name, allow_zero=False)
        if self.lower_price_limit is None and self.upper_price_limit is None:
            raise ValueError("price-limit facts require at least one supplied bound")


@dataclass(frozen=True)
class ContractFacts:
    """One source-aware current/future concrete-contract fact set.

    ``reference_price``, ``margin``, ``fee`` and ``price_limits`` are optional
    because they are only present "when provided".  A missing optional fact
    remains ``None`` (UNKNOWN), never a fabricated zero.
    """

    identity: ContractIdentity
    multiplier: Decimal
    tick_size: Decimal
    tick_unit: str
    currency: str
    observed_at: datetime
    source: SourceProvenance
    category: FactCategory
    freshness: FactFreshness
    reference_price: Decimal | None = None
    margin: MarginFacts | None = None
    fee: FeeModel | None = None
    price_limits: PriceLimitFacts | None = None
    effective_at: datetime | None = None
    is_historical_only: bool = False
    notes: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.identity, ContractIdentity):
            raise ValueError("contract facts identity must be a ContractIdentity")
        for value, name in (
            (self.multiplier, "contract facts multiplier"),
            (self.tick_size, "contract facts tick size"),
        ):
            _positive_or_zero_decimal(value, name, allow_zero=False)
        _required_text(self.tick_unit, "contract facts tick unit")
        _required_text(self.currency, "contract facts currency")
        if self.observed_at.tzinfo is None:
            raise ValueError("contract facts observed timestamp must be timezone-aware")
        if self.effective_at is not None and self.effective_at.tzinfo is None:
            raise ValueError("contract facts effective timestamp must be timezone-aware")
        if not isinstance(self.source, SourceProvenance):
            raise ValueError("contract facts source must be a SourceProvenance")
        if not isinstance(self.category, FactCategory):
            raise ValueError("contract facts category must be a FactCategory")
        if not isinstance(self.freshness, FactFreshness):
            raise ValueError("contract facts freshness must be a FactFreshness")
        if self.reference_price is not None:
            _positive_or_zero_decimal(self.reference_price, "contract facts reference price", allow_zero=False)
        if self.margin is not None and not isinstance(self.margin, MarginFacts):
            raise ValueError("contract facts margin must be a MarginFacts or None")
        if self.fee is not None and not isinstance(self.fee, FeeModel):
            raise ValueError("contract facts fee must be a FeeModel or None")
        if self.price_limits is not None and not isinstance(self.price_limits, PriceLimitFacts):
            raise ValueError("contract facts price limits must be a PriceLimitFacts or None")
        if type(self.is_historical_only) is not bool:
            raise ValueError("contract facts is_historical_only must be a bool")
        if not isinstance(self.notes, str):
            raise ValueError("contract facts notes must be a string")
        if self.is_historical_only and self.freshness is FactFreshness.CURRENT:
            raise ValueError("historical-only facts can never be labeled CURRENT")
        if (
            self.source.source_type is FactSourceType.HISTORICAL_CANONICAL_METADATA
            and self.freshness is FactFreshness.CURRENT
        ):
            raise ValueError("historical canonical metadata can never be labeled CURRENT broker truth")
        if (
            self.source.source_type is FactSourceType.HISTORICAL_CANONICAL_METADATA
            and not self.is_historical_only
        ):
            raise ValueError("historical canonical metadata facts must be marked is_historical_only")

    @property
    def tick_value(self) -> Decimal:
        """Currency per lot per tick (multiplier x tick size)."""
        return self.multiplier * self.tick_size

    def notional_per_lot(self, price: Decimal) -> Decimal:
        """Contract value in currency for one lot at the given price."""
        _positive_or_zero_decimal(price, "contract facts notional price", allow_zero=False)
        return price * self.multiplier

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "identity": self.identity.identity_id,
                "multiplier": _canonical_decimal(self.multiplier),
                "tick_size": _canonical_decimal(self.tick_size),
                "tick_unit": self.tick_unit,
                "currency": self.currency,
                "observed_at": self.observed_at.isoformat(),
                "effective_at": None if self.effective_at is None else self.effective_at.isoformat(),
                "source": {
                    "source_identity": self.source.source_identity,
                    "source_type": self.source.source_type.value,
                    "retrieved_at": self.source.retrieved_at.isoformat(),
                    "source_version": self.source.source_version,
                    "notes": self.source.notes,
                },
                "category": self.category.value,
                "freshness": self.freshness.value,
                "reference_price": _canonical_decimal(self.reference_price),
                "margin": _margin_identity_payload(self.margin),
                "fee": _fee_identity_payload(self.fee),
                "price_limits": _price_limit_identity_payload(self.price_limits),
                "is_historical_only": self.is_historical_only,
                "notes": self.notes,
            }
        )


def current_use_eligibility(facts: ContractFacts) -> tuple[bool, str]:
    """Whether a fact set may be used as CURRENT execution truth (fail closed).

    Only an EXCHANGE/BROKER FACT with ``CURRENT`` freshness that is not
    historical-only is eligible.  Scenario assumptions, behavior observations,
    policy constraints, stale/unknown freshness and historical-only metadata
    all fail closed.
    """
    if not isinstance(facts, ContractFacts):
        raise ValueError("current-use eligibility requires a ContractFacts")
    if facts.category is not FactCategory.EXCHANGE_BROKER_FACT:
        return False, "NOT_EXCHANGE_BROKER_FACT"
    if facts.is_historical_only:
        return False, "HISTORICAL_ONLY_FACTS_ARE_NOT_CURRENT_TRUTH"
    if facts.freshness is FactFreshness.CURRENT:
        return True, "CURRENT"
    if facts.freshness is FactFreshness.STALE:
        return False, "STALE"
    return False, "UNKNOWN"

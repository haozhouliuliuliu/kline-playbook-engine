"""Synthetic, point-in-time China-futures contract semantics for validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
from typing import Iterable


def _contract_hash(value: object) -> str:
    encoded = json.dumps(value, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


class OrderAction(str, Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"


class PositionDirection(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class CloseOffset(str, Enum):
    CLOSE_TODAY = "CLOSE_TODAY"
    CLOSE_PREVIOUS = "CLOSE_PREVIOUS"
    CLOSE = "CLOSE"


@dataclass(frozen=True)
class ContractSpecification:
    exchange: str
    product_family: str
    instrument_id: str
    listed_at: datetime
    deactivated_at: datetime
    contract_multiplier: Decimal
    minimum_price_tick: Decimal
    currency: str
    unit: str
    price_limit_rule_identity: str | None
    offset_fee_metadata_identity: str
    metadata_version: str

    def __post_init__(self) -> None:
        required = (
            self.exchange,
            self.product_family,
            self.instrument_id,
            self.currency,
            self.unit,
            self.offset_fee_metadata_identity,
            self.metadata_version,
        )
        if not all(required):
            raise ValueError("contract specification has required empty fields")
        if self.listed_at.tzinfo is None or self.deactivated_at.tzinfo is None:
            raise ValueError("contract lifecycle timestamps must be timezone-aware")
        if self.deactivated_at <= self.listed_at:
            raise ValueError("contract deactivation must follow listing")
        decimals = (self.contract_multiplier, self.minimum_price_tick)
        if any(type(value) is not Decimal or value <= 0 for value in decimals):
            raise ValueError("contract multiplier and minimum tick must be positive Decimals")

    def is_active_at(self, timestamp: datetime) -> bool:
        if timestamp.tzinfo is None:
            raise ValueError("contract lifecycle check requires a timezone-aware timestamp")
        return self.listed_at <= timestamp < self.deactivated_at

    def is_on_tick(self, price: Decimal) -> bool:
        if type(price) is not Decimal or price <= 0:
            raise ValueError("price must be a positive Decimal")
        return price % self.minimum_price_tick == 0

    @property
    def identity_id(self) -> str:
        return _contract_hash(
            {
                "exchange": self.exchange,
                "product_family": self.product_family,
                "instrument_id": self.instrument_id,
                "listed_at": self.listed_at.isoformat(),
                "deactivated_at": self.deactivated_at.isoformat(),
                "contract_multiplier": str(self.contract_multiplier),
                "minimum_price_tick": str(self.minimum_price_tick),
                "currency": self.currency,
                "unit": self.unit,
                "price_limit_rule_identity": self.price_limit_rule_identity,
                "offset_fee_metadata_identity": self.offset_fee_metadata_identity,
                "metadata_version": self.metadata_version,
            }
        )


@dataclass(frozen=True)
class ContractMaster:
    """Immutable explicit concrete-contract catalog."""

    version: str
    _specifications: tuple[ContractSpecification, ...]

    def __init__(self, version: str, specifications: Iterable[ContractSpecification]) -> None:
        if not version:
            raise ValueError("contract master version is required")
        object.__setattr__(self, "version", version)
        ordered = tuple(sorted(specifications, key=lambda item: item.instrument_id))
        if not ordered:
            raise ValueError("contract master requires at least one concrete contract")
        if len({item.instrument_id for item in ordered}) != len(ordered):
            raise ValueError("concrete contract identifiers must be unique")
        object.__setattr__(self, "_specifications", ordered)

    @property
    def specifications(self) -> tuple[ContractSpecification, ...]:
        return self._specifications

    def get(self, instrument_id: str) -> ContractSpecification | None:
        return next((item for item in self._specifications if item.instrument_id == instrument_id), None)

    @property
    def identity_id(self) -> str:
        return _contract_hash(
            {
                "version": self.version,
                "contracts": [item.identity_id for item in self._specifications],
            }
        )


@dataclass(frozen=True)
class ContractMappingEntry:
    research_symbol: str
    concrete_instrument_id: str
    effective_at: datetime
    effective_until: datetime
    available_at: datetime
    mapping_version: str

    def __post_init__(self) -> None:
        if not all((self.research_symbol, self.concrete_instrument_id, self.mapping_version)):
            raise ValueError("contract mapping identities are required")
        timestamps = (self.effective_at, self.effective_until, self.available_at)
        if any(value.tzinfo is None for value in timestamps):
            raise ValueError("contract mapping timestamps must be timezone-aware")
        if self.effective_until <= self.effective_at:
            raise ValueError("contract mapping end must follow its effective time")

    def is_usable_at(self, timestamp: datetime) -> bool:
        if timestamp.tzinfo is None:
            raise ValueError("mapping resolution requires a timezone-aware timestamp")
        return self.available_at <= timestamp and self.effective_at <= timestamp < self.effective_until

    @property
    def identity_id(self) -> str:
        return _contract_hash(
            {
                "research_symbol": self.research_symbol,
                "concrete_instrument_id": self.concrete_instrument_id,
                "effective_at": self.effective_at.isoformat(),
                "effective_until": self.effective_until.isoformat(),
                "available_at": self.available_at.isoformat(),
                "mapping_version": self.mapping_version,
            }
        )


@dataclass(frozen=True)
class ContractMappingSchedule:
    """Explicit PIT schedule; it contains no contract-selection algorithm."""

    version: str
    research_symbols: tuple[str, ...]
    _entries: tuple[ContractMappingEntry, ...]

    def __init__(
        self,
        version: str,
        research_symbols: Iterable[str],
        entries: Iterable[ContractMappingEntry],
    ) -> None:
        if not version:
            raise ValueError("contract mapping schedule version is required")
        symbols = tuple(sorted(set(research_symbols)))
        if not symbols or any(not symbol for symbol in symbols):
            raise ValueError("mapping schedule requires explicit research symbols")
        ordered = tuple(
            sorted(
                entries,
                key=lambda item: (item.research_symbol, item.effective_at, item.available_at, item.identity_id),
            )
        )
        if any(item.research_symbol not in symbols for item in ordered):
            raise ValueError("mapping entry uses an undeclared research abstraction")
        if len({item.identity_id for item in ordered}) != len(ordered):
            raise ValueError("duplicate contract mapping entries are not allowed")
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "research_symbols", symbols)
        object.__setattr__(self, "_entries", ordered)

    @property
    def entries(self) -> tuple[ContractMappingEntry, ...]:
        return self._entries

    @property
    def identity_id(self) -> str:
        return _contract_hash(
            {
                "version": self.version,
                "research_symbols": self.research_symbols,
                "entries": [item.identity_id for item in self._entries],
            }
        )


@dataclass(frozen=True)
class ContractResolution:
    request_id: str
    requested_symbol: str
    concrete_instrument_id: str
    contract_identity_id: str
    contract_master_identity_id: str
    mapping_schedule_identity_id: str | None
    mapping_entry_identity_id: str | None
    resolved_at: datetime

    @property
    def identity_id(self) -> str:
        return _contract_hash(
            {
                "request_id": self.request_id,
                "requested_symbol": self.requested_symbol,
                "concrete_instrument_id": self.concrete_instrument_id,
                "contract_identity_id": self.contract_identity_id,
                "contract_master_identity_id": self.contract_master_identity_id,
                "mapping_schedule_identity_id": self.mapping_schedule_identity_id,
                "mapping_entry_identity_id": self.mapping_entry_identity_id,
                "resolved_at": self.resolved_at.isoformat(),
            }
        )


class ContractResolver:
    def __init__(self, master: ContractMaster, schedule: ContractMappingSchedule) -> None:
        self.master = master
        self.schedule = schedule

    def resolve(self, request_id: str, requested_symbol: str, decision_at: datetime) -> ContractResolution:
        if not request_id or not requested_symbol:
            raise ValueError("contract resolution request identity and symbol are required")
        concrete = self.master.get(requested_symbol)
        mapping_entry = None
        if requested_symbol in self.schedule.research_symbols:
            matches = [
                item
                for item in self.schedule.entries
                if item.research_symbol == requested_symbol and item.is_usable_at(decision_at)
            ]
            if len(matches) != 1:
                raise ValueError("contract mapping must resolve point-in-time to exactly one concrete contract")
            mapping_entry = matches[0]
            concrete = self.master.get(mapping_entry.concrete_instrument_id)
        elif concrete is None:
            raise ValueError("requested symbol is neither an explicit concrete contract nor a mapped abstraction")
        if concrete is None:
            raise ValueError("contract mapping target is missing from the contract master")
        if not concrete.is_active_at(decision_at):
            raise ValueError("concrete contract is not active at the decision time")
        return ContractResolution(
            request_id,
            requested_symbol,
            concrete.instrument_id,
            concrete.identity_id,
            self.master.identity_id,
            self.schedule.identity_id if mapping_entry else None,
            mapping_entry.identity_id if mapping_entry else None,
            decision_at,
        )


@dataclass(frozen=True)
class PriceLimitFact:
    fact_id: str
    concrete_instrument_id: str
    contract_identity_id: str
    trading_day: date
    lower_price: Decimal
    upper_price: Decimal
    observed_at: datetime
    available_at: datetime
    rule_identity: str
    locked: bool = False

    def __post_init__(self) -> None:
        if not all((self.fact_id, self.concrete_instrument_id, self.contract_identity_id, self.rule_identity)):
            raise ValueError("price-limit fact identities are required")
        if self.observed_at.tzinfo is None or self.available_at.tzinfo is None:
            raise ValueError("price-limit fact timestamps must be timezone-aware")
        if self.available_at < self.observed_at:
            raise ValueError("price-limit fact cannot be available before observation")
        prices = (self.lower_price, self.upper_price)
        if any(type(value) is not Decimal or value <= 0 for value in prices):
            raise ValueError("price-limit bounds must be positive Decimals")
        if self.upper_price < self.lower_price:
            raise ValueError("price-limit upper bound cannot be below the lower bound")

    @property
    def identity_id(self) -> str:
        return _contract_hash(
            {
                "fact_id": self.fact_id,
                "concrete_instrument_id": self.concrete_instrument_id,
                "contract_identity_id": self.contract_identity_id,
                "trading_day": self.trading_day.isoformat(),
                "lower_price": str(self.lower_price),
                "upper_price": str(self.upper_price),
                "observed_at": self.observed_at.isoformat(),
                "available_at": self.available_at.isoformat(),
                "rule_identity": self.rule_identity,
                "locked": self.locked,
            }
        )


@dataclass(frozen=True)
class OffsetCostAssumptions:
    model_version: str
    close_today_fee_per_unit: Decimal
    close_previous_fee_per_unit: Decimal
    generic_close_rule: str = "TODAY_FIRST"

    def __post_init__(self) -> None:
        if not self.model_version:
            raise ValueError("offset-cost model version is required")
        fees = (self.close_today_fee_per_unit, self.close_previous_fee_per_unit)
        if any(type(value) is not Decimal or value < 0 for value in fees):
            raise ValueError("synthetic offset fees must be non-negative Decimals")
        if self.generic_close_rule != "TODAY_FIRST":
            raise ValueError("unsupported synthetic generic close rule")

    @property
    def identity_id(self) -> str:
        return _contract_hash(
            {
                "model_version": self.model_version,
                "close_today_fee_per_unit": str(self.close_today_fee_per_unit),
                "close_previous_fee_per_unit": str(self.close_previous_fee_per_unit),
                "generic_close_rule": self.generic_close_rule,
            }
        )

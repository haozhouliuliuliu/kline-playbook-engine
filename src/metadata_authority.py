"""Governed historical metadata authority for the canonical dataset.

Every outcome-affecting metadata fact binds:
- source URL / resource identity;
- retrieval timestamp;
- artifact SHA256 where applicable;
- effective period;
- schema/version.

No weekday/holiday inference and no manual session guesses: trading-day and
session facts come only from bound official artifacts.  Facts that cannot yet
be bound to an official artifact are classified explicitly (OFFICIAL_PARTIAL)
and never silently assumed.

This module is the minimum historical metadata authority for the selected
BALANCED product/coverage window.  It contains no credentials and no raw
market data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from hashlib import sha256
import json
import re
from typing import Iterable
from zoneinfo import ZoneInfo

from src.data_substrate import SessionMetadata, SessionWindow

_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def canonical_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _required_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")


@dataclass(frozen=True)
class GovernedSource:
    """Binding metadata for one official source artifact (or explicit pending)."""

    resource_identity: str
    url: str
    retrieved_at: datetime
    artifact_sha256: str | None
    schema_version: str
    classification: str
    effective_period_start: date
    effective_period_end: date

    def __post_init__(self) -> None:
        for value, name in (
            (self.resource_identity, "governed source resource identity"),
            (self.url, "governed source URL"),
            (self.schema_version, "governed source schema version"),
            (self.classification, "governed source classification"),
        ):
            _required_text(value, name)
        if self.retrieved_at.tzinfo is None:
            raise ValueError("governed source retrieval timestamp must be timezone-aware")
        if self.artifact_sha256 is not None and not _SHA256.fullmatch(self.artifact_sha256):
            raise ValueError("governed source artifact SHA256 must be 64 lowercase hex characters")
        if self.effective_period_end < self.effective_period_start:
            raise ValueError("governed source effective period end must follow its start")
        if self.classification not in {
            "OFFICIAL_AVAILABLE",
            "OFFICIAL_PARTIAL",
            "ARCHIVED_OFFICIAL",
            "PENDING_OFFICIAL_BINDING",
        }:
            raise ValueError("governed source classification is not recognized")

    def identity(self) -> str:
        return canonical_hash(
            {
                "resource_identity": self.resource_identity,
                "url": self.url,
                "retrieved_at": self.retrieved_at.isoformat(),
                "artifact_sha256": self.artifact_sha256,
                "schema_version": self.schema_version,
                "classification": self.classification,
                "effective_period_start": self.effective_period_start.isoformat(),
                "effective_period_end": self.effective_period_end.isoformat(),
            }
        )


@dataclass(frozen=True)
class ContractSpec:
    """Official contract specification fact (tick, multiplier, quote, months)."""

    exchange: str
    product: str
    trading_code: str
    tick: Decimal
    tick_unit: str
    multiplier: Decimal
    multiplier_unit: str
    quote_unit: str
    contract_months: str
    price_limit_pct: str
    source: GovernedSource

    def __post_init__(self) -> None:
        for value, name in (
            (self.exchange, "contract spec exchange"),
            (self.product, "contract spec product"),
            (self.trading_code, "contract spec trading code"),
            (self.tick_unit, "contract spec tick unit"),
            (self.multiplier_unit, "contract spec multiplier unit"),
            (self.quote_unit, "contract spec quote unit"),
            (self.contract_months, "contract spec contract months"),
            (self.price_limit_pct, "contract spec price limit"),
        ):
            _required_text(value, name)
        for value, name in ((self.tick, "contract spec tick"), (self.multiplier, "contract spec multiplier")):
            if type(value) is not Decimal or not value.is_finite() or value <= 0:
                raise ValueError(f"{name} must be a positive finite Decimal")

    def identity(self) -> str:
        return canonical_hash(
            {
                "exchange": self.exchange,
                "product": self.product,
                "trading_code": self.trading_code,
                "tick": str(self.tick),
                "tick_unit": self.tick_unit,
                "multiplier": str(self.multiplier),
                "multiplier_unit": self.multiplier_unit,
                "quote_unit": self.quote_unit,
                "contract_months": self.contract_months,
                "price_limit_pct": self.price_limit_pct,
                "source_identity": self.source.identity(),
            }
        )


@dataclass(frozen=True)
class ProductSessionSchedule:
    """Official day + night session schedule for a product/effective period."""

    exchange: str
    product: str
    effective_period_start: date
    effective_period_end: date
    day_windows: tuple[tuple[time, time], ...]
    night_window: tuple[time, time] | None
    timezone: str = "Asia/Shanghai"
    source: GovernedSource | None = None

    def __post_init__(self) -> None:
        for value, name in ((self.exchange, "session schedule exchange"), (self.product, "session schedule product")):
            _required_text(value, name)
        if self.effective_period_end < self.effective_period_start:
            raise ValueError("session schedule effective period end must follow its start")
        if not self.day_windows:
            raise ValueError("session schedule requires at least one day window")
        for start, end in self.day_windows:
            if not isinstance(start, time) or not isinstance(end, time) or end <= start:
                raise ValueError("session schedule day windows must be (start < end) time pairs")
        if self.night_window is not None:
            start, end = self.night_window
            if not isinstance(start, time) or not isinstance(end, time):
                raise ValueError("session schedule night window must be a time pair")

    def identity(self) -> str:
        return canonical_hash(
            {
                "exchange": self.exchange,
                "product": self.product,
                "effective_period_start": self.effective_period_start.isoformat(),
                "effective_period_end": self.effective_period_end.isoformat(),
                "day_windows": [[s.isoformat(), e.isoformat()] for s, e in self.day_windows],
                "night_window": (
                    None
                    if self.night_window is None
                    else [self.night_window[0].isoformat(), self.night_window[1].isoformat()]
                ),
                "timezone": self.timezone,
                "source_identity": None if self.source is None else self.source.identity(),
            }
        )


class TradingCalendar:
    """Set of official trading days bound to official artifacts."""

    def __init__(
        self,
        version: str,
        days: Iterable[date],
        source: GovernedSource,
    ) -> None:
        if not version.strip():
            raise ValueError("trading calendar version is required")
        self.version = version
        self._days = frozenset(days)
        if not self._days:
            raise ValueError("trading calendar requires at least one trading day")
        self.source = source

    def is_trading_day(self, day: date) -> bool:
        return day in self._days

    def trading_days(self, start: date, end: date) -> tuple[date, ...]:
        if end < start:
            raise ValueError("trading-day range end must follow its start")
        return tuple(sorted(day for day in self._days if start <= day <= end))

    def previous_trading_day(self, day: date) -> date | None:
        candidates = sorted(d for d in self._days if d < day)
        return candidates[-1] if candidates else None

    def identity(self) -> str:
        return canonical_hash(
            {
                "version": self.version,
                "days": sorted(d.isoformat() for d in self._days),
                "source_identity": self.source.identity(),
            }
        )


def session_windows_for_trading_day(
    calendar: TradingCalendar,
    schedule: ProductSessionSchedule,
    concrete_contract: str,
    trading_day: date,
    *,
    night_closed_days: frozenset[date] = frozenset(),
) -> tuple[SessionWindow, ...]:
    """Build explicit session windows for one contract/trading-day.

    Night session belongs to the trading day it opens for and starts 21:00 of
    the previous trading day (official SHFE rule).  If the trading day is in
    the governed night-closed set, no night window is emitted.  No weekday or
    holiday inference is performed.
    """
    if not calendar.is_trading_day(trading_day):
        raise ValueError(f"{trading_day.isoformat()} is not an official trading day")
    zone = ZoneInfo(schedule.timezone)
    windows: list[SessionWindow] = []
    if schedule.night_window is not None and trading_day not in night_closed_days:
        prev = calendar.previous_trading_day(trading_day)
        if prev is not None:
            night_start_t, night_end_t = schedule.night_window
            start = datetime.combine(prev, night_start_t, tzinfo=zone)
            end = datetime.combine(trading_day, night_end_t, tzinfo=zone)
            if night_end_t < night_start_t or night_end_t <= time(12, 0):
                # night window crosses midnight: end is on the trading day
                pass
            windows.append(SessionWindow(schedule.exchange, concrete_contract, trading_day, start, end, "night"))
    for day_start_t, day_end_t in schedule.day_windows:
        start = datetime.combine(trading_day, day_start_t, tzinfo=zone)
        end = datetime.combine(trading_day, day_end_t, tzinfo=zone)
        windows.append(SessionWindow(schedule.exchange, concrete_contract, trading_day, start, end, "day"))
    return tuple(sorted(windows, key=lambda w: w.start))


def build_session_metadata(
    calendar: TradingCalendar,
    schedule: ProductSessionSchedule,
    concrete_contract: str,
    trading_days: Iterable[date],
    *,
    night_closed_days: frozenset[date] = frozenset(),
) -> SessionMetadata:
    """Build the explicit SessionMetadata for one contract across trading days."""
    windows: list[SessionWindow] = []
    for day in sorted(trading_days):
        windows.extend(
            session_windows_for_trading_day(
                calendar, schedule, concrete_contract, day, night_closed_days=night_closed_days
            )
        )
    return SessionMetadata(schedule.identity(), windows)


@dataclass(frozen=True)
class ContractUniverseEntry:
    """A listed concrete contract with governed listing/expiry boundaries."""

    exchange: str
    product: str
    concrete_contract: str
    first_trading_day: date
    last_trading_day: date
    source: GovernedSource | None = None

    def __post_init__(self) -> None:
        for value, name in (
            (self.exchange, "contract universe exchange"),
            (self.product, "contract universe product"),
            (self.concrete_contract, "contract universe concrete contract"),
        ):
            _required_text(value, name)
        if not self.concrete_contract.startswith(self.exchange + "."):
            raise ValueError("contract universe exchange and contract disagree")
        if self.last_trading_day < self.first_trading_day:
            raise ValueError("contract universe listing boundary end must follow its start")

    def identity(self) -> str:
        return canonical_hash(
            {
                "exchange": self.exchange,
                "product": self.product,
                "concrete_contract": self.concrete_contract,
                "first_trading_day": self.first_trading_day.isoformat(),
                "last_trading_day": self.last_trading_day.isoformat(),
                "source_identity": None if self.source is None else self.source.identity(),
            }
        )

"""Outcome-blind deterministic historical slice selector for replay V0.1.

The selector receives only calendar, mapping, eligibility, session and partition
identity facts. Its input types intentionally contain no OHLC, return, volatility,
PnL, regime or news fields, so historical outcome cannot participate in selection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from hashlib import sha256
import json
from typing import Iterable, Sequence


SELECTOR_VERSION = "KPE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_SELECTOR_V0_1"
PRODUCT_ORDER = ("cu", "al", "ni", "au", "ag", "rb")
PRIOR_HISTORY_TRADING_DAYS = 20
BURN_IN_TRADING_DAYS = 2
MEASUREMENT_TRADING_DAYS = 20
REPLAY_TRADING_DAYS = BURN_IN_TRADING_DAYS + MEASUREMENT_TRADING_DAYS


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _non_empty(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be non-empty")
    return value


@dataclass(frozen=True)
class ReplayMappingFact:
    product: str
    trading_day: date
    concrete_contract: str
    mapping_identity: str

    def __post_init__(self) -> None:
        if self.product not in PRODUCT_ORDER:
            raise ValueError("mapping product is outside the accepted replay product order")
        _non_empty(self.concrete_contract, "concrete_contract")
        _non_empty(self.mapping_identity, "mapping_identity")


@dataclass(frozen=True)
class ReplayPartitionFact:
    product: str
    concrete_contract: str
    trading_day: date
    partition_identity: str
    session_identity: str
    eligible: bool = True

    def __post_init__(self) -> None:
        if self.product not in PRODUCT_ORDER:
            raise ValueError("partition product is outside the accepted replay product order")
        _non_empty(self.concrete_contract, "concrete_contract")
        _non_empty(self.partition_identity, "partition_identity")
        _non_empty(self.session_identity, "session_identity")
        if type(self.eligible) is not bool:
            raise ValueError("eligible must be a strict bool")


@dataclass(frozen=True)
class ReplaySlice:
    product: str
    concrete_contract: str
    prior_history_days: tuple[date, ...]
    burn_in_days: tuple[date, ...]
    measurement_days: tuple[date, ...]
    mapping_identities: tuple[str, ...]
    partition_identities: tuple[str, ...]
    session_identities: tuple[str, ...]
    selector_version: str = SELECTOR_VERSION
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if self.product not in PRODUCT_ORDER:
            raise ValueError("slice product is outside accepted order")
        _non_empty(self.concrete_contract, "concrete_contract")
        if len(self.prior_history_days) != PRIOR_HISTORY_TRADING_DAYS:
            raise ValueError("slice must bind exactly 20 prior history trading days")
        if len(self.burn_in_days) != BURN_IN_TRADING_DAYS:
            raise ValueError("slice must bind exactly 2 burn-in trading days")
        if len(self.measurement_days) != MEASUREMENT_TRADING_DAYS:
            raise ValueError("slice must bind exactly 20 measurement trading days")
        all_replay_days = self.burn_in_days + self.measurement_days
        if len(self.mapping_identities) != len(all_replay_days):
            raise ValueError("slice must bind one mapping identity per replay day")
        total_days = PRIOR_HISTORY_TRADING_DAYS + REPLAY_TRADING_DAYS
        if len(self.partition_identities) != total_days:
            raise ValueError("slice must bind one selected-contract partition per history/replay day")
        if len(self.session_identities) != total_days:
            raise ValueError("slice must bind one session identity per history/replay day")
        object.__setattr__(
            self,
            "identity",
            _hash(
                {
                    "selector_version": self.selector_version,
                    "product": self.product,
                    "concrete_contract": self.concrete_contract,
                    "prior_history_days": [item.isoformat() for item in self.prior_history_days],
                    "burn_in_days": [item.isoformat() for item in self.burn_in_days],
                    "measurement_days": [item.isoformat() for item in self.measurement_days],
                    "mapping_identities": self.mapping_identities,
                    "partition_identities": self.partition_identities,
                    "session_identities": self.session_identities,
                }
            ),
        )


def select_v0_1_slice(
    *,
    trading_calendar: Sequence[date],
    mappings: Iterable[ReplayMappingFact],
    partitions: Iterable[ReplayPartitionFact],
) -> ReplaySlice:
    """Return the first mechanically eligible slice in accepted product/date order."""
    calendar = tuple(trading_calendar)
    if len(calendar) < PRIOR_HISTORY_TRADING_DAYS + REPLAY_TRADING_DAYS:
        raise ValueError("trading calendar is too short for V0.1")
    if any(not isinstance(day, date) for day in calendar):
        raise ValueError("trading calendar must contain date values")
    if tuple(sorted(set(calendar))) != calendar:
        raise ValueError("trading calendar must be strictly increasing and unique")

    mapping_index: dict[tuple[str, date], ReplayMappingFact] = {}
    for item in mappings:
        key = (item.product, item.trading_day)
        if key in mapping_index:
            raise ValueError("duplicate replay mapping fact")
        mapping_index[key] = item

    partition_index: dict[tuple[str, str, date], ReplayPartitionFact] = {}
    for item in partitions:
        key = (item.product, item.concrete_contract, item.trading_day)
        if key in partition_index:
            raise ValueError("duplicate replay partition fact")
        partition_index[key] = item

    for product in PRODUCT_ORDER:
        for replay_start in range(PRIOR_HISTORY_TRADING_DAYS, len(calendar) - REPLAY_TRADING_DAYS + 1):
            prior_days = calendar[replay_start - PRIOR_HISTORY_TRADING_DAYS : replay_start]
            replay_days = calendar[replay_start : replay_start + REPLAY_TRADING_DAYS]
            replay_mappings = tuple(mapping_index.get((product, day)) for day in replay_days)
            if any(item is None for item in replay_mappings):
                continue
            concrete_contracts = {item.concrete_contract for item in replay_mappings if item is not None}
            if len(concrete_contracts) != 1:
                continue
            concrete_contract = next(iter(concrete_contracts))
            all_days = prior_days + replay_days
            selected_partitions = tuple(
                partition_index.get((product, concrete_contract, day)) for day in all_days
            )
            if any(item is None or not item.eligible for item in selected_partitions):
                continue

            replay_mappings_checked = tuple(item for item in replay_mappings if item is not None)
            selected_partitions_checked = tuple(item for item in selected_partitions if item is not None)
            return ReplaySlice(
                product=product,
                concrete_contract=concrete_contract,
                prior_history_days=prior_days,
                burn_in_days=replay_days[:BURN_IN_TRADING_DAYS],
                measurement_days=replay_days[BURN_IN_TRADING_DAYS:],
                mapping_identities=tuple(item.mapping_identity for item in replay_mappings_checked),
                partition_identities=tuple(item.partition_identity for item in selected_partitions_checked),
                session_identities=tuple(item.session_identity for item in selected_partitions_checked),
            )

    raise ValueError("no eligible deterministic V0.1 replay slice exists")


__all__ = [
    "BURN_IN_TRADING_DAYS",
    "MEASUREMENT_TRADING_DAYS",
    "PRIOR_HISTORY_TRADING_DAYS",
    "PRODUCT_ORDER",
    "REPLAY_TRADING_DAYS",
    "ReplayMappingFact",
    "ReplayPartitionFact",
    "ReplaySlice",
    "SELECTOR_VERSION",
    "select_v0_1_slice",
]

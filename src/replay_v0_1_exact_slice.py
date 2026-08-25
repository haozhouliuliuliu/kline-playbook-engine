"""Exact V0.1 slice sealing from accepted local corpus + frozen authorities.

This adapter intentionally remains outcome-blind. It reads only the accepted
historical manifest, official trading/session metadata, and the frozen E07
source-governed mapping schedule. Price, return, volatility, PnL and news are
not inputs.

A trading day is admitted to the mapping surface only when the source-governed
concrete contract is identical at the first and final governed session instant.
That matters for SHFE night-session products: an E07 switch effective at 09:00
can make the same trading day span two contracts (previous-night session versus
day session). Such a day is omitted rather than collapsed to one date-level
mapping.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence
from zoneinfo import ZoneInfo

from src.historical_manifest import DatasetManifest
from src.replay_v0_1_selector import (
    PRODUCT_ORDER,
    ReplayMappingFact,
    ReplayPartitionFact,
    ReplaySlice,
    select_v0_1_slice,
)


EXACT_SLICE_ADAPTER_VERSION = "KPE_REPLAY_V0_1_EXACT_SLICE_ADAPTER_V0_1"
_CONTRACT = re.compile(r"^SHFE\.([a-z]+)\d{4}$")
_SHANGHAI = ZoneInfo("Asia/Shanghai")


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _require_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty text")
    return value.strip()


def _parse_time(value: str) -> time:
    return time.fromisoformat(value)


def _parse_calendar(payload: Mapping[str, Any]) -> tuple[tuple[date, ...], frozenset[date], str]:
    raw_days = payload.get("trading_days")
    if not isinstance(raw_days, Mapping):
        raise ValueError("canonical trading calendar has no trading_days mapping")
    days: list[date] = []
    for year in sorted(raw_days):
        values = raw_days[year]
        if not isinstance(values, list):
            raise ValueError("canonical trading calendar year must contain a list")
        days.extend(date.fromisoformat(item) for item in values)
    calendar = tuple(days)
    if tuple(sorted(set(calendar))) != calendar:
        raise ValueError("canonical trading days must be unique and strictly increasing")

    raw_night_closed = payload.get("night_closed_trading_days", {})
    if not isinstance(raw_night_closed, Mapping):
        raise ValueError("night_closed_trading_days must be a mapping")
    night_closed: set[date] = set()
    for values in raw_night_closed.values():
        if not isinstance(values, list):
            raise ValueError("night-closed calendar year must contain a list")
        night_closed.update(date.fromisoformat(item) for item in values)
    if not night_closed.issubset(set(calendar)):
        raise ValueError("night-closed trading day is outside canonical calendar")

    calendar_identity = _require_text(payload.get("identity"), "calendar identity")
    return calendar, frozenset(night_closed), calendar_identity


def _parse_session_schedule(payload: Mapping[str, Any]) -> tuple[dict[str, dict[str, Any]], str]:
    products = payload.get("products")
    if not isinstance(products, Mapping):
        raise ValueError("session schedule has no products mapping")
    result: dict[str, dict[str, Any]] = {}
    for product in PRODUCT_ORDER:
        record = products.get(product)
        if not isinstance(record, Mapping):
            raise ValueError(f"session schedule missing {product}")
        day_windows = record.get("day_windows")
        if not isinstance(day_windows, list) or not day_windows:
            raise ValueError(f"session schedule {product} has no day windows")
        night_window = record.get("night_window")
        if not isinstance(night_window, list) or len(night_window) != 2:
            raise ValueError(f"session schedule {product} has no exact night window")
        timezone = _require_text(record.get("timezone"), f"{product} timezone")
        if timezone != "Asia/Shanghai":
            raise ValueError("V0.1 SHFE session timezone must be Asia/Shanghai")
        result[product] = {
            "day_start": _parse_time(day_windows[0][0]),
            "day_end": _parse_time(day_windows[-1][1]),
            "night_start": _parse_time(night_window[0]),
            "identity": _require_text(record.get("identity"), f"{product} session identity"),
        }
    return result, _require_text(payload.get("root_identity"), "session root identity")


@dataclass(frozen=True)
class _E07Record:
    product: str
    concrete_contract: str
    effective_at: datetime
    available_at: datetime
    record_identity: str

    def __post_init__(self) -> None:
        if self.product not in PRODUCT_ORDER:
            raise ValueError("E07 product is outside accepted replay order")
        if self.effective_at.tzinfo is None or self.available_at.tzinfo is None:
            raise ValueError("E07 timestamps must be timezone-aware")
        if self.available_at > self.effective_at:
            raise ValueError("E07 mapping cannot become available after switch")
        if not _CONTRACT.fullmatch(self.concrete_contract):
            raise ValueError("E07 target must be a concrete SHFE contract")
        _require_text(self.record_identity, "E07 record identity")


def _parse_e07(payload: Mapping[str, Any]) -> tuple[dict[str, tuple[_E07Record, ...]], str]:
    if payload.get("price_data_used") != "NO" or payload.get("candidate_outcome_data_used") != "NO":
        raise ValueError("E07 exact-slice input must remain outcome blind")
    semantics = payload.get("semantics")
    if not isinstance(semantics, Mapping) or semantics.get("derivation") != "SOURCE_GOVERNED":
        raise ValueError("E07 derivation must be SOURCE_GOVERNED")
    schedule_identity = _require_text(payload.get("schedule_identity"), "E07 schedule identity")
    raw_records = payload.get("records")
    if not isinstance(raw_records, list) or not raw_records:
        raise ValueError("E07 evidence has no mapping records")

    by_product: dict[str, list[_E07Record]] = {item: [] for item in PRODUCT_ORDER}
    for item in raw_records:
        if not isinstance(item, Mapping):
            raise ValueError("E07 record must be an object")
        research_symbol = _require_text(item.get("research_symbol"), "E07 research symbol")
        prefix = "MAIN:SHFE:"
        if not research_symbol.startswith(prefix):
            raise ValueError("E07 research symbol is outside SHFE main namespace")
        product = research_symbol[len(prefix):]
        record = _E07Record(
            product=product,
            concrete_contract=_require_text(item.get("concrete_instrument_id"), "E07 concrete contract"),
            effective_at=datetime.fromisoformat(_require_text(item.get("effective_at"), "E07 effective_at")),
            available_at=datetime.fromisoformat(_require_text(item.get("available_at"), "E07 available_at")),
            record_identity=_require_text(item.get("record_identity"), "E07 record identity"),
        )
        if record.effective_at.date() != date.fromisoformat(
            _require_text(item.get("effective_trading_date"), "E07 effective trading date")
        ):
            raise ValueError("E07 effective date disagrees with effective_at")
        by_product[product].append(record)

    normalized: dict[str, tuple[_E07Record, ...]] = {}
    for product, records in by_product.items():
        ordered = tuple(sorted(records, key=lambda item: (item.effective_at, item.record_identity)))
        if not ordered:
            raise ValueError(f"E07 evidence has no records for {product}")
        normalized[product] = ordered
    return normalized, schedule_identity


def _record_at(records: Sequence[_E07Record], instant: datetime) -> _E07Record | None:
    eligible = [
        item for item in records
        if item.available_at <= instant and item.effective_at <= instant
    ]
    if not eligible:
        return None
    return max(eligible, key=lambda item: (item.effective_at, item.record_identity))


def build_full_session_mapping_facts(
    *,
    trading_calendar: Sequence[date],
    night_closed_days: frozenset[date],
    session_products: Mapping[str, Mapping[str, Any]],
    e07_records: Mapping[str, Sequence[_E07Record]],
    e07_schedule_identity: str,
) -> tuple[ReplayMappingFact, ...]:
    """Expand E07 only onto days with one concrete contract for the full session.

    For a normal night-session trading day the first governed instant is the
    previous trading day's night-session start. If an E07 switch at 09:00 makes
    first-session and final-session contracts differ, that day is intentionally
    absent from the returned mapping facts and therefore cannot enter a replay
    window.
    """
    calendar = tuple(trading_calendar)
    facts: list[ReplayMappingFact] = []
    for index, day in enumerate(calendar):
        for product in PRODUCT_ORDER:
            session = session_products[product]
            if day in night_closed_days:
                first_instant = datetime.combine(day, session["day_start"], tzinfo=_SHANGHAI)
            else:
                if index == 0:
                    continue
                previous_trading_day = calendar[index - 1]
                first_instant = datetime.combine(
                    previous_trading_day, session["night_start"], tzinfo=_SHANGHAI
                )
            final_instant = datetime.combine(day, session["day_end"], tzinfo=_SHANGHAI)
            first_record = _record_at(e07_records[product], first_instant)
            final_record = _record_at(e07_records[product], final_instant)
            if first_record is None or final_record is None:
                continue
            if first_record.concrete_contract != final_record.concrete_contract:
                # Intra-trading-day source-governed roll. There is no legal
                # single-contract day-level fact for V0.1.
                continue
            mapping_identity = _hash(
                {
                    "adapter_version": EXACT_SLICE_ADAPTER_VERSION,
                    "schedule_identity": e07_schedule_identity,
                    "product": product,
                    "trading_day": day.isoformat(),
                    "first_instant": first_instant.isoformat(),
                    "final_instant": final_instant.isoformat(),
                    "first_record_identity": first_record.record_identity,
                    "final_record_identity": final_record.record_identity,
                    "concrete_contract": first_record.concrete_contract,
                }
            )
            facts.append(
                ReplayMappingFact(
                    product=product,
                    trading_day=day,
                    concrete_contract=first_record.concrete_contract,
                    mapping_identity=mapping_identity,
                )
            )
    return tuple(facts)


def build_manifest_partition_facts(manifest: DatasetManifest) -> tuple[ReplayPartitionFact, ...]:
    facts: list[ReplayPartitionFact] = []
    for partition in manifest.partitions:
        match = _CONTRACT.fullmatch(partition.contract)
        if match is None:
            continue
        product = match.group(1)
        if product not in PRODUCT_ORDER:
            continue
        if partition.granularity_seconds != 60 or partition.exchange != "SHFE":
            continue
        facts.append(
            ReplayPartitionFact(
                product=product,
                concrete_contract=partition.contract,
                trading_day=partition.trading_day,
                partition_identity=partition.identity(),
                session_identity=partition.session_metadata_version,
                eligible=partition.quality_status == "PASS",
            )
        )
    return tuple(facts)


@dataclass(frozen=True)
class ExactReplaySliceSeal:
    slice: ReplaySlice
    canonical_corpus_identity: str
    raw_manifest_root_identity: str
    trading_calendar_identity: str
    session_authority_root_identity: str
    e07_schedule_identity: str
    adapter_version: str = EXACT_SLICE_ADAPTER_VERSION
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        for value, name in (
            (self.canonical_corpus_identity, "canonical corpus identity"),
            (self.raw_manifest_root_identity, "raw manifest root identity"),
            (self.trading_calendar_identity, "trading calendar identity"),
            (self.session_authority_root_identity, "session authority root identity"),
            (self.e07_schedule_identity, "E07 schedule identity"),
        ):
            _require_text(value, name)
        object.__setattr__(
            self,
            "identity",
            _hash(
                {
                    "adapter_version": self.adapter_version,
                    "slice_identity": self.slice.identity,
                    "canonical_corpus_identity": self.canonical_corpus_identity,
                    "raw_manifest_root_identity": self.raw_manifest_root_identity,
                    "trading_calendar_identity": self.trading_calendar_identity,
                    "session_authority_root_identity": self.session_authority_root_identity,
                    "e07_schedule_identity": self.e07_schedule_identity,
                }
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "adapter_version": self.adapter_version,
            "exact_slice_seal_identity": self.identity,
            "slice_identity": self.slice.identity,
            "canonical_corpus_identity": self.canonical_corpus_identity,
            "raw_manifest_root_identity": self.raw_manifest_root_identity,
            "trading_calendar_identity": self.trading_calendar_identity,
            "session_authority_root_identity": self.session_authority_root_identity,
            "e07_schedule_identity": self.e07_schedule_identity,
            "product": self.slice.product,
            "concrete_contract": self.slice.concrete_contract,
            "prior_history_days": [item.isoformat() for item in self.slice.prior_history_days],
            "burn_in_days": [item.isoformat() for item in self.slice.burn_in_days],
            "measurement_days": [item.isoformat() for item in self.slice.measurement_days],
            "mapping_identities": list(self.slice.mapping_identities),
            "partition_identities": list(self.slice.partition_identities),
            "session_identities": list(self.slice.session_identities),
        }


def select_and_seal_exact_v0_1_slice(
    *,
    manifest_path: Path,
    trading_calendar_path: Path,
    session_schedule_path: Path,
    e07_path: Path,
    corpus_identity_path: Path,
) -> ExactReplaySliceSeal:
    manifest = DatasetManifest.load(manifest_path)
    corpus = _load_json(corpus_identity_path)
    expected_manifest_identity = _require_text(
        corpus.get("raw_manifest_root_identity"), "accepted raw manifest root identity"
    )
    if manifest.identity() != expected_manifest_identity:
        raise ValueError("local canonical manifest identity does not match accepted corpus authority")
    expected_count = corpus.get("partition_count")
    if type(expected_count) is not int or expected_count != len(manifest.partitions):
        raise ValueError("local canonical manifest partition count disagrees with accepted corpus authority")

    calendar_payload = _load_json(trading_calendar_path)
    session_payload = _load_json(session_schedule_path)
    e07_payload = _load_json(e07_path)
    calendar, night_closed, calendar_identity = _parse_calendar(calendar_payload)
    sessions, session_root_identity = _parse_session_schedule(session_payload)
    e07_records, e07_schedule_identity = _parse_e07(e07_payload)

    mappings = build_full_session_mapping_facts(
        trading_calendar=calendar,
        night_closed_days=night_closed,
        session_products=sessions,
        e07_records=e07_records,
        e07_schedule_identity=e07_schedule_identity,
    )
    partitions = build_manifest_partition_facts(manifest)
    selected = select_v0_1_slice(
        trading_calendar=calendar,
        mappings=mappings,
        partitions=partitions,
    )
    return ExactReplaySliceSeal(
        slice=selected,
        canonical_corpus_identity=_require_text(
            corpus.get("canonical_corpus_identity"), "canonical corpus identity"
        ),
        raw_manifest_root_identity=expected_manifest_identity,
        trading_calendar_identity=calendar_identity,
        session_authority_root_identity=session_root_identity,
        e07_schedule_identity=e07_schedule_identity,
    )


__all__ = [
    "EXACT_SLICE_ADAPTER_VERSION",
    "ExactReplaySliceSeal",
    "build_full_session_mapping_facts",
    "build_manifest_partition_facts",
    "select_and_seal_exact_v0_1_slice",
]

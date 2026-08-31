"""Source-neutral runtime contract-facts ingestion, cache and snapshot selection.

This module is the runtime companion to ``src.contract_facts``.  It provides a
source-neutral store that (offline only, no live acquisition, no credentials,
no broker/exchange awareness, no paid calls):

- accepts fully-provenanced ``ContractFacts`` snapshots and gives each snapshot
  an immutable, deterministic content identity;
- records the exact contract, source identity/type and the observed /
  retrieved / effective timestamps of the fact set;
- classifies each snapshot COMPLETE / INCOMPLETE against the fact fields
  required for a full current one-lot evaluation (reference price, resolvable
  margin, fee);
- computes effective freshness (CURRENT / STALE / UNKNOWN) as of an arbitrary
  query time, including an optional wall-clock expiry;
- atomically replaces a known complete current snapshot only with a newer,
  not-lower-quality complete snapshot, and rejects older / lower-quality /
  incomplete snapshots so they can never silently displace it;
- keeps historical-only and non-exchange fact sets in a separate partition so
  a historical fact can never be mislabeled or served as current
  broker/account truth;
- answers "eligible current facts for exact contract X as of time T" with
  either the eligible snapshot (provenance retained through selection) or a
  reason-coded INSUFFICIENT / STALE / UNKNOWN / INCOMPLETE result.

There is intentionally no source-less latest-wins path: every stored snapshot
carries an explicit ``SourceProvenance`` and the query never synthesises a
winner without it.

The store is an offline, single-process, non-thread-safe cache.  It performs
no acquisition and no trading decision.  No permanent numeric risk rules, no
production default contract facts, no fee/margin/slippage defaults live here.
All numeric values in tests that exercise this module are synthetic
FIXTURE-ONLY values and are never exported as production defaults.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json

from src.contract_facts import (
    ContractFacts,
    ContractIdentity,
    FactCategory,
    FactFreshness,
    SourceProvenance,
    current_use_eligibility,
)


def _canonical_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _required_text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")


def _optional_identity_text(value: object, name: str) -> None:
    if value is not None:
        _required_text(value, name)


class SnapshotStatus(str, Enum):
    """Runtime selection state for an exact-contract query.

    Only ``CURRENT`` is eligible for live current use; everything else fails
    closed with an explicit reason code.
    """

    CURRENT = "CURRENT"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"
    INCOMPLETE = "INCOMPLETE"
    INSUFFICIENT = "INSUFFICIENT"


class SnapshotReasonCode(str, Enum):
    """Structured reason codes (not free text) for a snapshot query."""

    ELIGIBLE = "ELIGIBLE"
    NO_SNAPSHOT_FOR_CONTRACT = "NO_SNAPSHOT_FOR_CONTRACT"
    SNAPSHOT_STALE = "SNAPSHOT_STALE"
    SNAPSHOT_EXPIRED = "SNAPSHOT_EXPIRED"
    SNAPSHOT_FRESHNESS_UNKNOWN = "SNAPSHOT_FRESHNESS_UNKNOWN"
    SNAPSHOT_INCOMPLETE = "SNAPSHOT_INCOMPLETE"
    SNAPSHOT_HISTORICAL_ONLY = "SNAPSHOT_HISTORICAL_ONLY"
    SNAPSHOT_NOT_EXCHANGE_BROKER_FACT = "SNAPSHOT_NOT_EXCHANGE_BROKER_FACT"
    SESSION_IDENTITY_MISMATCH = "SESSION_IDENTITY_MISMATCH"
    TRADING_DAY_MISMATCH = "TRADING_DAY_MISMATCH"
    QUERY_IDENTITY_MISMATCH = "QUERY_IDENTITY_MISMATCH"


class SnapshotRecordStatus(str, Enum):
    """Outcome of a snapshot record/ingestion attempt."""

    STORED = "STORED"
    REPLACED = "REPLACED"
    REJECTED = "REJECTED"
    STORED_HISTORICAL = "STORED_HISTORICAL"


class SnapshotRecordReasonCode(str, Enum):
    """Structured reason codes (not free text) for a snapshot record attempt."""

    STORED_FIRST = "STORED_FIRST"
    REPLACED_NEWER_COMPLETE_CURRENT = "REPLACED_NEWER_COMPLETE_CURRENT"
    REPLACED_UPGRADE = "REPLACED_UPGRADE"
    REJECTED_OLDER = "REJECTED_OLDER"
    REJECTED_LOWER_QUALITY = "REJECTED_LOWER_QUALITY"
    REJECTED_INCOMPLETE_REPLACING_COMPLETE = "REJECTED_INCOMPLETE_REPLACING_COMPLETE"
    STORED_HISTORICAL = "STORED_HISTORICAL"


class SnapshotQuality(str, Enum):
    """Quality classification used for deterministic replacement ordering."""

    HISTORICAL_ONLY = "HISTORICAL_ONLY"  # never current truth; separate partition
    INCOMPLETE = "INCOMPLETE"  # missing facts required for a full current evaluation
    COMPLETE_NOT_CURRENT = "COMPLETE_NOT_CURRENT"  # complete but STALE/UNKNOWN freshness
    COMPLETE_CURRENT = "COMPLETE_CURRENT"  # complete and CURRENT (protected top state)


def snapshot_completeness(facts: ContractFacts) -> tuple[bool, tuple[str, ...]]:
    """Whether a fact set is COMPLETE for a full current one-lot evaluation.

    Required fields: reference price, a margin fact resolvable to a per-lot
    amount, and a fee model.  A missing required field stays missing (None),
    never a fabricated zero.  Price limits are optional for completeness.
    """
    if not isinstance(facts, ContractFacts):
        raise ValueError("snapshot completeness requires a ContractFacts")
    missing: list[str] = []
    if facts.reference_price is None:
        missing.append("reference_price")
    if facts.margin is None:
        missing.append("margin")
    else:
        if facts.reference_price is not None:
            notional = facts.notional_per_lot(facts.reference_price)
            if facts.margin.one_lot_margin_amount(notional) is None:
                missing.append("margin_resolvable")
    if facts.fee is None:
        missing.append("fee")
    return (not missing), tuple(missing)


def effective_freshness(
    facts_or_expiry: ContractFacts | "ContractFactsSnapshot",
    as_of: datetime,
) -> FactFreshness:
    """Effective freshness of a fact set / snapshot as of an arbitrary time.

    A fact set declared CURRENT but expired by the supplied wall-clock time is
    STALE (fail closed).  UNKNOWN freshness stays UNKNOWN; STALE stays STALE.
    """
    if as_of.tzinfo is None:
        raise ValueError("effective-freshness query time must be timezone-aware")
    if isinstance(facts_or_expiry, ContractFacts):
        return facts_or_expiry.freshness
    snapshot = facts_or_expiry
    if snapshot.expires_at is not None and as_of >= snapshot.expires_at:
        return FactFreshness.STALE
    return snapshot.facts.freshness


def _snapshot_quality(snapshot: "ContractFactsSnapshot") -> SnapshotQuality:
    facts = snapshot.facts
    if facts.is_historical_only or facts.category is not FactCategory.EXCHANGE_BROKER_FACT:
        return SnapshotQuality.HISTORICAL_ONLY
    if not snapshot.is_complete:
        return SnapshotQuality.INCOMPLETE
    if effective_freshness(snapshot, snapshot.recorded_at) is FactFreshness.CURRENT:
        return SnapshotQuality.COMPLETE_CURRENT
    return SnapshotQuality.COMPLETE_NOT_CURRENT


def _quality_rank(snapshot: "ContractFactsSnapshot") -> int:
    """Monotonic ordering for replacement: higher is strictly better."""
    quality = _snapshot_quality(snapshot)
    return {
        SnapshotQuality.HISTORICAL_ONLY: 0,
        SnapshotQuality.INCOMPLETE: 1,
        SnapshotQuality.COMPLETE_NOT_CURRENT: 2,
        SnapshotQuality.COMPLETE_CURRENT: 3,
    }[quality]


def _snapshot_content(snapshot: "ContractFactsSnapshot") -> dict[str, object]:
    facts = snapshot.facts
    margin = facts.margin
    fee = facts.fee
    limits = facts.price_limits
    return {
        "facts_identity": facts.identity_id,
        "multiplier": str(facts.multiplier),
        "tick_size": str(facts.tick_size),
        "tick_unit": facts.tick_unit,
        "currency": facts.currency,
        "reference_price": None if facts.reference_price is None else str(facts.reference_price),
        "margin": None
        if margin is None
        else {
            "basis": margin.basis.value,
            "initial_margin_per_lot": (
                None if margin.initial_margin_per_lot is None else str(margin.initial_margin_per_lot)
            ),
            "maintenance_margin_per_lot": (
                None
                if margin.maintenance_margin_per_lot is None
                else str(margin.maintenance_margin_per_lot)
            ),
            "initial_margin_percent": (
                None
                if margin.initial_margin_percent is None
                else str(margin.initial_margin_percent)
            ),
            "maintenance_margin_percent": (
                None
                if margin.maintenance_margin_percent is None
                else str(margin.maintenance_margin_percent)
            ),
            "currency": margin.currency,
        },
        "fee": None
        if fee is None
        else {
            "commission_per_lot": (
                None if fee.commission_per_lot is None else str(fee.commission_per_lot)
            ),
            "commission_percent": (
                None if fee.commission_percent is None else str(fee.commission_percent)
            ),
            "currency": fee.currency,
        },
        "price_limits": None
        if limits is None
        else {
            "lower_price_limit": (
                None if limits.lower_price_limit is None else str(limits.lower_price_limit)
            ),
            "upper_price_limit": (
                None if limits.upper_price_limit is None else str(limits.upper_price_limit)
            ),
            "basis": limits.basis,
            "currency": limits.currency,
        },
        "observed_at": facts.observed_at.isoformat(),
        "effective_at": None if facts.effective_at is None else facts.effective_at.isoformat(),
        "source": {
            "source_identity": facts.source.source_identity,
            "source_type": facts.source.source_type.value,
            "retrieved_at": facts.source.retrieved_at.isoformat(),
            "source_version": facts.source.source_version,
            "notes": facts.source.notes,
        },
        "category": facts.category.value,
        "freshness": facts.freshness.value,
        "is_historical_only": facts.is_historical_only,
        "notes": facts.notes,
        "recorded_at": snapshot.recorded_at.isoformat(),
        "expires_at": None if snapshot.expires_at is None else snapshot.expires_at.isoformat(),
        "session_identity": snapshot.session_identity,
        "trading_day": snapshot.trading_day,
        "query_identity": snapshot.query_identity,
        "is_complete": snapshot.is_complete,
        "missing_facts": list(snapshot.missing_facts),
    }


@dataclass(frozen=True)
class ContractFactsSnapshot:
    """One immutable, source-provenanced fact snapshot in the runtime store.

    The snapshot identity is a deterministic content hash over the full fact
    set plus every snapshot metadata field, so any change to facts or metadata
    changes the identity.  ``is_complete`` and ``missing_facts`` are derived
    from the facts at construction and re-validated, so an incomplete snapshot
    can never be relabeled complete.
    """

    facts: ContractFacts
    recorded_at: datetime
    expires_at: datetime | None
    is_complete: bool
    missing_facts: tuple[str, ...]
    session_identity: str | None
    trading_day: str | None
    query_identity: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.facts, ContractFacts):
            raise ValueError("snapshot facts must be a ContractFacts")
        if self.recorded_at.tzinfo is None:
            raise ValueError("snapshot recorded timestamp must be timezone-aware")
        if self.expires_at is not None and self.expires_at.tzinfo is None:
            raise ValueError("snapshot expiry timestamp must be timezone-aware")
        _optional_identity_text(self.session_identity, "snapshot session identity")
        _optional_identity_text(self.trading_day, "snapshot trading-day identity")
        _optional_identity_text(self.query_identity, "snapshot query identity")
        if type(self.is_complete) is not bool:
            raise ValueError("snapshot is_complete must be a bool")
        if not isinstance(self.missing_facts, tuple) or not all(
            isinstance(item, str) for item in self.missing_facts
        ):
            raise ValueError("snapshot missing facts must be a tuple of strings")
        derived_complete, derived_missing = snapshot_completeness(self.facts)
        if self.is_complete != derived_complete or self.missing_facts != derived_missing:
            raise ValueError(
                "snapshot completeness is inconsistent with its facts (tamper/fabrication guard)"
            )

    @property
    def snapshot_id(self) -> str:
        """Immutable deterministic content identity (sha256 hex)."""
        return _canonical_hash(_snapshot_content(self))

    @property
    def contract_identity(self) -> ContractIdentity:
        return self.facts.identity

    @property
    def contract_identity_id(self) -> str:
        return self.facts.identity.identity_id

    @property
    def observed_at(self) -> datetime:
        return self.facts.observed_at

    @property
    def retrieved_at(self) -> datetime:
        return self.facts.source.retrieved_at

    @property
    def effective_at(self) -> datetime | None:
        return self.facts.effective_at

    @property
    def provenance(self) -> SourceProvenance:
        return self.facts.source

    @property
    def quality(self) -> SnapshotQuality:
        return _snapshot_quality(self)


@dataclass(frozen=True)
class SnapshotRecordOutcome:
    """Deterministic outcome of a snapshot record/ingestion attempt."""

    status: SnapshotRecordStatus
    reason_code: SnapshotRecordReasonCode
    previous_snapshot_id: str | None = None
    current_snapshot_id: str | None = None
    contract_identity_id: str | None = None


@dataclass(frozen=True)
class SnapshotQueryResult:
    """Deterministic answer to "eligible current facts for exact contract X as
    of time T".

    ``snapshot`` is non-None only when the query is ELIGIBLE; ``provenance``
    is retained through selection so the caller always sees the source that
    produced the answer (no source-less latest-wins).
    """

    status: SnapshotStatus
    reason_code: SnapshotReasonCode
    as_of: datetime
    snapshot: ContractFactsSnapshot | None = None
    provenance: SourceProvenance | None = None
    missing_facts: tuple[str, ...] = ()
    eligibility_reason: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.status, SnapshotStatus):
            raise ValueError("snapshot query status must be a SnapshotStatus")
        if not isinstance(self.reason_code, SnapshotReasonCode):
            raise ValueError("snapshot query reason code must be a SnapshotReasonCode")
        if self.as_of.tzinfo is None:
            raise ValueError("snapshot query as-of time must be timezone-aware")
        if self.snapshot is not None and not isinstance(self.snapshot, ContractFactsSnapshot):
            raise ValueError("snapshot query snapshot must be a ContractFactsSnapshot or None")
        if self.provenance is not None and not isinstance(self.provenance, SourceProvenance):
            raise ValueError("snapshot query provenance must be a SourceProvenance or None")
        if not isinstance(self.missing_facts, tuple) or not all(
            isinstance(item, str) for item in self.missing_facts
        ):
            raise ValueError("snapshot query missing facts must be a tuple of strings")
        if self.eligibility_reason is not None and not isinstance(self.eligibility_reason, str):
            raise ValueError("snapshot query eligibility reason must be a string or None")


def make_snapshot(
    facts: ContractFacts,
    *,
    recorded_at: datetime | None = None,
    expires_at: datetime | None = None,
    session_identity: str | None = None,
    trading_day: str | None = None,
    query_identity: str | None = None,
) -> ContractFactsSnapshot:
    """Build an immutable snapshot from a fact set (completeness derived).

    ``recorded_at`` defaults to the fact set's source retrieval timestamp so
    construction is deterministic when the caller does not supply one.
    """
    if recorded_at is None:
        recorded_at = facts.source.retrieved_at
    is_complete, missing_facts = snapshot_completeness(facts)
    return ContractFactsSnapshot(
        facts=facts,
        recorded_at=recorded_at,
        expires_at=expires_at,
        is_complete=is_complete,
        missing_facts=missing_facts,
        session_identity=session_identity,
        trading_day=trading_day,
        query_identity=query_identity,
    )


class ContractFactsStore:
    """Source-neutral runtime ingestion/cache/snapshot-selection store.

    State is keyed by exact contract identity.  ``_current`` holds the best
    known current-truth candidate per contract; ``_historical`` holds
    historical-only / non-exchange snapshots that can never be served as
    current broker/account truth; ``_superseded`` retains accepted
    current-candidate snapshots that were later replaced (audit provenance).

    Replacement is deterministic and fail closed: an older, lower-quality or
    incomplete snapshot is rejected and can never silently displace a known
    complete current snapshot.  The store is not thread-safe (offline use).
    """

    def __init__(self) -> None:
        self._current: dict[str, ContractFactsSnapshot] = {}
        self._historical: dict[str, tuple[ContractFactsSnapshot, ...]] = {}
        self._superseded: dict[str, tuple[ContractFactsSnapshot, ...]] = {}

    # -- ingestion ---------------------------------------------------------

    def record(self, snapshot: ContractFactsSnapshot) -> SnapshotRecordOutcome:
        """Ingest one snapshot with atomic, deterministic replacement policy."""
        if not isinstance(snapshot, ContractFactsSnapshot):
            raise ValueError("store record requires a ContractFactsSnapshot")

        contract_id = snapshot.contract_identity_id
        facts = snapshot.facts

        # Historical-only and non-exchange fact sets are recorded in a separate
        # partition and can never become the current candidate.
        if facts.is_historical_only or facts.category is not FactCategory.EXCHANGE_BROKER_FACT:
            existing_historical = self._historical.get(contract_id, ())
            self._historical[contract_id] = existing_historical + (snapshot,)
            return SnapshotRecordOutcome(
                status=SnapshotRecordStatus.STORED_HISTORICAL,
                reason_code=SnapshotRecordReasonCode.STORED_HISTORICAL,
                current_snapshot_id=(
                    None if contract_id not in self._current else self._current[contract_id].snapshot_id
                ),
                contract_identity_id=contract_id,
            )

        existing = self._current.get(contract_id)
        if existing is None:
            self._current[contract_id] = snapshot
            return SnapshotRecordOutcome(
                status=SnapshotRecordStatus.STORED,
                reason_code=SnapshotRecordReasonCode.STORED_FIRST,
                current_snapshot_id=snapshot.snapshot_id,
                contract_identity_id=contract_id,
            )

        status, reason = _decide_replacement(existing, snapshot)
        if status is SnapshotRecordStatus.REPLACED:
            self._superseded[contract_id] = self._superseded.get(contract_id, ()) + (existing,)
            self._current[contract_id] = snapshot
        return SnapshotRecordOutcome(
            status=status,
            reason_code=reason,
            previous_snapshot_id=existing.snapshot_id,
            current_snapshot_id=(
                snapshot.snapshot_id
                if status is SnapshotRecordStatus.REPLACED
                else existing.snapshot_id
            ),
            contract_identity_id=contract_id,
        )

    # -- selection ---------------------------------------------------------

    def query(
        self,
        contract_identity: ContractIdentity,
        as_of: datetime,
        *,
        session_identity: str | None = None,
        trading_day: str | None = None,
        query_identity: str | None = None,
    ) -> SnapshotQueryResult:
        """Eligible current facts for the exact contract as of ``as_of``."""
        if not isinstance(contract_identity, ContractIdentity):
            raise ValueError("store query requires a ContractIdentity")
        if as_of.tzinfo is None:
            raise ValueError("store query as-of time must be timezone-aware")
        _optional_identity_text(session_identity, "query session identity")
        _optional_identity_text(trading_day, "query trading-day identity")
        _optional_identity_text(query_identity, "query identity")

        contract_id = contract_identity.identity_id
        snapshot = self._current.get(contract_id)
        if snapshot is None:
            return SnapshotQueryResult(
                status=SnapshotStatus.INSUFFICIENT,
                reason_code=SnapshotReasonCode.NO_SNAPSHOT_FOR_CONTRACT,
                as_of=as_of,
            )

        if (
            session_identity is not None
            and snapshot.session_identity is not None
            and session_identity != snapshot.session_identity
        ):
            return SnapshotQueryResult(
                status=SnapshotStatus.INSUFFICIENT,
                reason_code=SnapshotReasonCode.SESSION_IDENTITY_MISMATCH,
                as_of=as_of,
                snapshot=snapshot,
                provenance=snapshot.provenance,
            )
        if (
            trading_day is not None
            and snapshot.trading_day is not None
            and trading_day != snapshot.trading_day
        ):
            return SnapshotQueryResult(
                status=SnapshotStatus.INSUFFICIENT,
                reason_code=SnapshotReasonCode.TRADING_DAY_MISMATCH,
                as_of=as_of,
                snapshot=snapshot,
                provenance=snapshot.provenance,
            )
        if (
            query_identity is not None
            and snapshot.query_identity is not None
            and query_identity != snapshot.query_identity
        ):
            return SnapshotQueryResult(
                status=SnapshotStatus.INSUFFICIENT,
                reason_code=SnapshotReasonCode.QUERY_IDENTITY_MISMATCH,
                as_of=as_of,
                snapshot=snapshot,
                provenance=snapshot.provenance,
            )

        if snapshot.facts.is_historical_only:
            return SnapshotQueryResult(
                status=SnapshotStatus.INSUFFICIENT,
                reason_code=SnapshotReasonCode.SNAPSHOT_HISTORICAL_ONLY,
                as_of=as_of,
                snapshot=snapshot,
                provenance=snapshot.provenance,
            )
        if snapshot.facts.category is not FactCategory.EXCHANGE_BROKER_FACT:
            return SnapshotQueryResult(
                status=SnapshotStatus.INSUFFICIENT,
                reason_code=SnapshotReasonCode.SNAPSHOT_NOT_EXCHANGE_BROKER_FACT,
                as_of=as_of,
                snapshot=snapshot,
                provenance=snapshot.provenance,
            )
        if not snapshot.is_complete:
            return SnapshotQueryResult(
                status=SnapshotStatus.INCOMPLETE,
                reason_code=SnapshotReasonCode.SNAPSHOT_INCOMPLETE,
                as_of=as_of,
                snapshot=snapshot,
                provenance=snapshot.provenance,
                missing_facts=snapshot.missing_facts,
            )

        freshness = effective_freshness(snapshot, as_of)
        if freshness is FactFreshness.CURRENT:
            _, eligibility_reason = current_use_eligibility(snapshot.facts)
            return SnapshotQueryResult(
                status=SnapshotStatus.CURRENT,
                reason_code=SnapshotReasonCode.ELIGIBLE,
                as_of=as_of,
                snapshot=snapshot,
                provenance=snapshot.provenance,
                eligibility_reason=eligibility_reason,
            )
        if freshness is FactFreshness.STALE:
            if snapshot.expires_at is not None and as_of >= snapshot.expires_at:
                reason = SnapshotReasonCode.SNAPSHOT_EXPIRED
            else:
                reason = SnapshotReasonCode.SNAPSHOT_STALE
            return SnapshotQueryResult(
                status=SnapshotStatus.STALE,
                reason_code=reason,
                as_of=as_of,
                snapshot=snapshot,
                provenance=snapshot.provenance,
            )
        return SnapshotQueryResult(
            status=SnapshotStatus.UNKNOWN,
            reason_code=SnapshotReasonCode.SNAPSHOT_FRESHNESS_UNKNOWN,
            as_of=as_of,
            snapshot=snapshot,
            provenance=snapshot.provenance,
        )

    # -- accessors ---------------------------------------------------------

    def current_snapshot(self, contract_identity: ContractIdentity) -> ContractFactsSnapshot | None:
        """Best known current-truth candidate for the exact contract (may be
        STALE/UNKNOWN/INCOMPLETE; use ``query`` for eligibility)."""
        if not isinstance(contract_identity, ContractIdentity):
            raise ValueError("store current-snapshot requires a ContractIdentity")
        return self._current.get(contract_identity.identity_id)

    def historical_snapshots(
        self, contract_identity: ContractIdentity
    ) -> tuple[ContractFactsSnapshot, ...]:
        """Historical-only / non-exchange snapshots retained for provenance."""
        if not isinstance(contract_identity, ContractIdentity):
            raise ValueError("store historical-snapshots requires a ContractIdentity")
        return self._historical.get(contract_identity.identity_id, ())

    def superseded_snapshots(
        self, contract_identity: ContractIdentity
    ) -> tuple[ContractFactsSnapshot, ...]:
        """Accepted current-candidate snapshots later replaced (audit)."""
        if not isinstance(contract_identity, ContractIdentity):
            raise ValueError("store superseded-snapshots requires a ContractIdentity")
        return self._superseded.get(contract_identity.identity_id, ())


def _decide_replacement(
    existing: ContractFactsSnapshot,
    incoming: ContractFactsSnapshot,
) -> tuple[SnapshotRecordStatus, SnapshotRecordReasonCode]:
    """Deterministic replacement policy for the current-candidate partition."""
    existing_rank = _quality_rank(existing)
    incoming_rank = _quality_rank(incoming)

    if incoming_rank < existing_rank:
        if incoming_rank <= 1 and existing_rank >= 2:
            return (
                SnapshotRecordStatus.REJECTED,
                SnapshotRecordReasonCode.REJECTED_INCOMPLETE_REPLACING_COMPLETE,
            )
        return (SnapshotRecordStatus.REJECTED, SnapshotRecordReasonCode.REJECTED_LOWER_QUALITY)

    if incoming_rank > existing_rank:
        return (SnapshotRecordStatus.REPLACED, SnapshotRecordReasonCode.REPLACED_UPGRADE)

    # Same quality rank: newer wins; equal-or-older is rejected (no silent churn).
    if incoming.recorded_at <= existing.recorded_at:
        return (SnapshotRecordStatus.REJECTED, SnapshotRecordReasonCode.REJECTED_OLDER)

    if incoming_rank == 3:
        return (
            SnapshotRecordStatus.REPLACED,
            SnapshotRecordReasonCode.REPLACED_NEWER_COMPLETE_CURRENT,
        )
    return (SnapshotRecordStatus.REPLACED, SnapshotRecordReasonCode.REPLACED_UPGRADE)


__all__ = [
    "SnapshotStatus",
    "SnapshotReasonCode",
    "SnapshotRecordStatus",
    "SnapshotRecordReasonCode",
    "SnapshotQuality",
    "ContractFactsSnapshot",
    "SnapshotRecordOutcome",
    "SnapshotQueryResult",
    "ContractFactsStore",
    "make_snapshot",
    "snapshot_completeness",
    "effective_freshness",
]

"""E07 source-governed TqSdk main-mapping prep: API-independent machinery.

Binding (Owner rule E-07, frozen):
    SOURCE_GOVERNED_TQSDK_MAIN_MAPPING
    APPLIED_TO_CANONICAL_CONCRETE_BARS

Scope of this module
--------------------
This module implements ONLY the ordinary engineering preparation that does NOT
require a real authenticated TqSdk session, and ONLY machinery that is
independent of the exact TqSdk API response contract.  It is the source-bound
artifact layer for the future source-governed historical main-contract mapping;
it is deliberately NOT wired into runtime execution (that remains a future,
Owner-gated package) and it does NOT replace the structural/synthetic
``ContractMappingSchedule`` in ``src.contract_semantics.py``.

Recorded E07 facts (see
``docs/evidence/E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_PREP_V0_1.md``):

    TQSDK_HISTORY_ACCESS=LOGIN_REQUIRED
    E07_MAPPING_COMPLETENESS=INCOMPLETE
    E07_RUNTIME_MAPPING_STATUS=FAIL_CLOSED_PREREQUISITE
    BLOCKED_API_CONTRACT_NOT_PINNED=YES

What is pinned and what is not
------------------------------
The existing evidence pins the vendor interface NAME and its documented
behaviour: ``TqApi.query_his_cont_quotes(symbol, n)`` returns, per effective
date, the underlying concrete contract for each 主连 (main) symbol; it requires
an authenticated ``TqApi`` session bound to ``TqAuth(account, password)``; the
vendor main symbols use the ``KQ.m@`` form; the source-defined switch applies at
the next trading day's open.  The evidence does NOT pin the exact wire/response
schema (field names, effective-date representation, record structure) of that
interface.  Per project policy this module therefore does NOT guess or implement
any TqSdk response decoding.  The decode boundary is declared
(``TqSdkMappingDecodeBoundary``) but deliberately NOT implemented, and the module
records ``BLOCKED_API_CONTRACT_NOT_PINNED``.

Owner rule enforcement
----------------------
    E07_PSEUDO_MAIN_PRICE_BARS=FORBIDDEN
    E07_PROJECT_AUTHORED_SUBSTITUTE=FORBIDDEN

The machinery enforces both: every mapped target must be a concrete contract id
(never a synthesized/pseudo-main symbol), and every record must carry the
``SOURCE_GOVERNED`` derivation marker (a project-authored OI/volume/calendar/PnL
substitution is rejected at construction).
"""

from __future__ import annotations

from collections.abc import Callable, Collection, Iterable
from dataclasses import dataclass
from datetime import date, datetime
from hashlib import sha256
import json
from typing import Protocol


# ---------------------------------------------------------------------------
# Blocked TqSdk API contract marker
# ---------------------------------------------------------------------------

BLOCKED_API_CONTRACT_NOT_PINNED = True
"""Exact ``query_his_cont_quotes`` response schema is not pinned by evidence.

While True, no TqSdk decode adapter may be implemented (per policy, do not
guess).  Only the API-independent machinery below is provided.
"""

TQSDK_DECODE_NOT_IMPLEMENTED = (
    "TqSdk query_his_cont_quotes response schema is not pinned; "
    "the decode adapter is deliberately not implemented (BLOCKED_API_CONTRACT_NOT_PINNED)"
)

PSEUDO_MAIN_MARKERS = ("@", ".main", "主连")
"""Markers that identify a vendor main/pseudo-main symbol (e.g. ``KQ.m@``)."""


def _mapping_hash(value: object) -> str:
    encoded = json.dumps(value, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Errors (fail closed)
# ---------------------------------------------------------------------------


class SourceGovernedMappingError(ValueError):
    """Base failure for source-governed mapping machinery."""


class MappingUnavailableError(SourceGovernedMappingError):
    """Fail closed: no source-governed record is effective at the decision time."""


class MappingConflictError(SourceGovernedMappingError):
    """Fail closed: two source-governed records conflict at the same effective day."""


class MappingSubstitutionForbidden(SourceGovernedMappingError):
    """Fail closed: project-authored mapping substitution is forbidden by Owner rule."""


class PseudoMainBarForbidden(SourceGovernedMappingError):
    """Fail closed: a synthesized/pseudo-main price bar may never be selected."""


def assert_source_governed_derivation(derivation: str) -> None:
    """Fail closed on any non-source-governed mapping derivation.

    Owner rule E-07 forbids substituting a project-authored OI/volume/calendar/
    PnL mapping rule for the source-governed artifact.  The only accepted
    derivation marker is ``SOURCE_GOVERNED``.
    """
    if derivation != "SOURCE_GOVERNED":
        raise MappingSubstitutionForbidden(
            f"mapping derivation must be SOURCE_GOVERNED, got {derivation!r}; "
            "project-authored OI/volume/calendar/PnL substitution is forbidden"
        )


def assert_not_pseudo_main_target(concrete_instrument_id: str) -> None:
    """Fail closed if a mapping target is a synthesized/pseudo-main symbol.

    The source-governed mapping may only select concrete contract bars that
    already exist in the canonical corpus; it must never create or point at
    pseudo-main price bars.
    """
    lowered = concrete_instrument_id.lower()
    if any(marker in lowered for marker in PSEUDO_MAIN_MARKERS):
        raise PseudoMainBarForbidden(
            f"mapping target {concrete_instrument_id!r} is a pseudo/main symbol; "
            "pseudo-main price bars are forbidden"
        )


def _require_clean_identity(value: str, field: str) -> str:
    if not value or value != value.strip():
        raise SourceGovernedMappingError(f"{field} must be a non-empty trimmed identity")
    return value


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MappingProvenance:
    """Provenance of a source-governed mapping record.

    ``source_artifact_identity`` is the hash of the exact source bytes/artifact
    when such bytes are bound; ``exact_bytes_bound`` must agree with it.  The
    E07 availability evidence already records
    ``DOC_FETCHED_BYTE_SHA256=NOT_RECORDED`` /
    ``PROVENANCE_LIMITATION=FETCHED_RENDERED_DOCS_NOT_RAW_RESPONSE_BYTES`` for
    the documentation retrieval; any future authenticated retrieval must bind
    exact response bytes here.
    """

    provider_identity: str
    interface_identity: str
    retrieval_session_id: str
    retrieved_at: datetime
    source_artifact_identity: str | None
    exact_bytes_bound: bool
    mapping_version: str
    provenance_notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field, value in (
            ("provider_identity", self.provider_identity),
            ("interface_identity", self.interface_identity),
            ("retrieval_session_id", self.retrieval_session_id),
            ("mapping_version", self.mapping_version),
        ):
            _require_clean_identity(value, field)
        if self.retrieved_at.tzinfo is None:
            raise SourceGovernedMappingError("retrieval timestamp must be timezone-aware")
        if self.exact_bytes_bound and not self.source_artifact_identity:
            raise SourceGovernedMappingError(
                "exact_bytes_bound=True requires a source artifact identity hash"
            )
        if not self.exact_bytes_bound and self.source_artifact_identity is not None:
            raise SourceGovernedMappingError(
                "source artifact identity requires exact_bytes_bound=True"
            )

    @property
    def identity_id(self) -> str:
        return _mapping_hash(
            {
                "provider_identity": self.provider_identity,
                "interface_identity": self.interface_identity,
                "retrieval_session_id": self.retrieval_session_id,
                "retrieved_at": self.retrieved_at.isoformat(),
                "source_artifact_identity": self.source_artifact_identity,
                "exact_bytes_bound": self.exact_bytes_bound,
                "mapping_version": self.mapping_version,
                "provenance_notes": self.provenance_notes,
            }
        )


# ---------------------------------------------------------------------------
# Source-governed mapping record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SourceGovernedMappingRecord:
    """One point-in-time source-governed mapping decision.

    Semantics follow the vendor's documented ``KQ.m@`` convention: the mapping
    is point-in-time and switches only at the source-defined next trading day's
    open.  ``effective_trading_date`` is the day the switch takes effect and
    ``effective_at`` is the exact switch moment (``effective_at.date()`` must
    equal ``effective_trading_date``).  ``available_at`` preserves
    point-in-time availability so a consumer never uses a record before the
    source made it available (no lookahead).
    """

    research_symbol: str
    source_symbol: str
    concrete_instrument_id: str
    effective_trading_date: date
    effective_at: datetime
    available_at: datetime
    provenance: MappingProvenance
    derivation: str = "SOURCE_GOVERNED"

    def __post_init__(self) -> None:
        for field, value in (
            ("research_symbol", self.research_symbol),
            ("source_symbol", self.source_symbol),
            ("concrete_instrument_id", self.concrete_instrument_id),
        ):
            _require_clean_identity(value, field)
        if self.research_symbol == self.source_symbol:
            raise SourceGovernedMappingError("research symbol must differ from the vendor source symbol")
        assert_source_governed_derivation(self.derivation)
        assert_not_pseudo_main_target(self.concrete_instrument_id)
        for field, value in (
            ("effective_at", self.effective_at),
            ("available_at", self.available_at),
        ):
            if value.tzinfo is None:
                raise SourceGovernedMappingError(f"{field} must be timezone-aware")
        if self.effective_at.date() != self.effective_trading_date:
            raise SourceGovernedMappingError(
                "effective_at must fall on the effective trading date "
                f"({self.effective_at.date()} != {self.effective_trading_date})"
            )
        if self.available_at > self.effective_at:
            raise SourceGovernedMappingError("a mapping record must be available no later than its switch")

    @property
    def identity_id(self) -> str:
        return _mapping_hash(
            {
                "research_symbol": self.research_symbol,
                "source_symbol": self.source_symbol,
                "concrete_instrument_id": self.concrete_instrument_id,
                "effective_trading_date": self.effective_trading_date.isoformat(),
                "effective_at": self.effective_at.isoformat(),
                "available_at": self.available_at.isoformat(),
                "provenance": self.provenance.identity_id,
                "derivation": self.derivation,
            }
        )

    def is_effective_at(self, decision_at: datetime) -> bool:
        if decision_at.tzinfo is None:
            raise SourceGovernedMappingError("mapping resolution requires a timezone-aware timestamp")
        return self.available_at <= decision_at and self.effective_at <= decision_at


# ---------------------------------------------------------------------------
# Membership validation facts
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MappingMembershipViolation:
    """A mapped concrete contract that is absent from the canonical universe."""

    research_symbol: str
    concrete_instrument_id: str
    effective_trading_date: date
    fact: str = "MAPPING_CONTRACT_NOT_IN_CANONICAL_UNIVERSE"

    @property
    def identity_id(self) -> str:
        return _mapping_hash(
            {
                "research_symbol": self.research_symbol,
                "concrete_instrument_id": self.concrete_instrument_id,
                "effective_trading_date": self.effective_trading_date.isoformat(),
                "fact": self.fact,
            }
        )


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SourceGovernedMappingResolution:
    """A single source-governed PIT resolution for a research symbol."""

    research_symbol: str
    concrete_instrument_id: str
    effective_trading_date: date
    effective_at: datetime
    resolved_at: datetime
    mapping_version: str
    record_identity_id: str
    schedule_identity_id: str
    provenance_identity_id: str

    @property
    def identity_id(self) -> str:
        return _mapping_hash(
            {
                "research_symbol": self.research_symbol,
                "concrete_instrument_id": self.concrete_instrument_id,
                "effective_trading_date": self.effective_trading_date.isoformat(),
                "effective_at": self.effective_at.isoformat(),
                "resolved_at": self.resolved_at.isoformat(),
                "mapping_version": self.mapping_version,
                "record_identity_id": self.record_identity_id,
                "schedule_identity_id": self.schedule_identity_id,
                "provenance_identity_id": self.provenance_identity_id,
            }
        )


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SourceGovernedMappingSchedule:
    """Deterministically normalized set of source-governed mapping records.

    Construction is deterministic: records are sorted by
    ``(research_symbol, effective_trading_date, effective_at, identity_id)`` and
    duplicated/conflicting effective days fail closed.  PIT resolution returns
    exactly the record whose switch is the latest one already effective; a
    missing record fails closed (``MappingUnavailableError``).
    """

    version: str
    research_symbols: tuple[str, ...]
    _records: tuple[SourceGovernedMappingRecord, ...]

    def __init__(
        self,
        version: str,
        research_symbols: Iterable[str],
        records: Iterable[SourceGovernedMappingRecord],
    ) -> None:
        _require_clean_identity(version, "version")
        symbols = tuple(sorted({_require_clean_identity(s, "research symbol") for s in research_symbols}))
        if not symbols:
            raise SourceGovernedMappingError("mapping schedule requires explicit research symbols")
        ordered = tuple(
            sorted(
                records,
                key=lambda r: (
                    r.research_symbol,
                    r.effective_trading_date,
                    r.effective_at,
                    r.identity_id,
                ),
            )
        )
        if any(r.research_symbol not in symbols for r in ordered):
            raise SourceGovernedMappingError("mapping record uses an undeclared research symbol")
        if len({r.identity_id for r in ordered}) != len(ordered):
            raise MappingConflictError("duplicate source-governed mapping records are not allowed")
        by_key: dict[tuple[str, date], set[str]] = {}
        for r in ordered:
            key = (r.research_symbol, r.effective_trading_date)
            by_key.setdefault(key, set()).add(r.identity_id)
            if len(by_key[key]) > 1:
                raise MappingConflictError(
                    "conflicting mapping records share an effective day for "
                    f"{r.research_symbol} on {r.effective_trading_date.isoformat()}"
                )
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "research_symbols", symbols)
        object.__setattr__(self, "_records", ordered)

    @property
    def records(self) -> tuple[SourceGovernedMappingRecord, ...]:
        return self._records

    @property
    def identity_id(self) -> str:
        return _mapping_hash(
            {
                "version": self.version,
                "research_symbols": self.research_symbols,
                "records": [r.identity_id for r in self._records],
            }
        )

    def resolve(self, research_symbol: str, decision_at: datetime) -> SourceGovernedMappingResolution:
        """Resolve the source-governed main contract at a point in time.

        Fail closed: raises ``MappingUnavailableError`` when no record applies
        and ``MappingConflictError`` on any residual ambiguity.
        """
        if decision_at.tzinfo is None:
            raise SourceGovernedMappingError("mapping resolution requires a timezone-aware timestamp")
        if research_symbol not in self.research_symbols:
            raise MappingUnavailableError(
                f"no source-governed mapping declared for research symbol {research_symbol!r}"
            )
        effective = [
            r for r in self._records
            if r.research_symbol == research_symbol and r.is_effective_at(decision_at)
        ]
        if not effective:
            raise MappingUnavailableError(
                "no source-governed mapping record is effective for "
                f"{research_symbol!r} at {decision_at.isoformat()}"
            )
        latest = max(effective, key=lambda r: r.effective_at)
        if sum(1 for r in effective if r.effective_at == latest.effective_at) != 1:
            raise MappingConflictError(
                f"ambiguous source-governed mapping for {research_symbol!r} "
                f"at {decision_at.isoformat()}"
            )
        return SourceGovernedMappingResolution(
            research_symbol=latest.research_symbol,
            concrete_instrument_id=latest.concrete_instrument_id,
            effective_trading_date=latest.effective_trading_date,
            effective_at=latest.effective_at,
            resolved_at=decision_at,
            mapping_version=latest.provenance.mapping_version,
            record_identity_id=latest.identity_id,
            schedule_identity_id=self.identity_id,
            provenance_identity_id=latest.provenance.identity_id,
        )

    def validate_canonical_membership(
        self, canonical_instruments: Collection[str]
    ) -> tuple[MappingMembershipViolation, ...]:
        """Return membership violations for targets outside the canonical universe.

        Records ``MAPPING_CONTRACT_NOT_IN_CANONICAL_UNIVERSE`` per offending
        record; it never substitutes another contract.
        """
        members = set(canonical_instruments)
        violations = []
        for r in self._records:
            if r.concrete_instrument_id not in members:
                violations.append(
                    MappingMembershipViolation(
                        research_symbol=r.research_symbol,
                        concrete_instrument_id=r.concrete_instrument_id,
                        effective_trading_date=r.effective_trading_date,
                    )
                )
        return tuple(violations)

    def assert_concrete_bar_selection_only(self, canonical_instruments: Collection[str]) -> None:
        """Fail closed if any record targets a non-canonical or pseudo-main bar."""
        violations = self.validate_canonical_membership(canonical_instruments)
        if violations:
            first = violations[0]
            raise PseudoMainBarForbidden(
                f"mapped concrete contract {first.concrete_instrument_id!r} is not in the "
                f"canonical universe ({first.fact}); substitution is forbidden"
            )


# ---------------------------------------------------------------------------
# Terminal-only auth capture boundary
# ---------------------------------------------------------------------------


class TerminalOnlyAuthCapture(Protocol):
    """Boundary for capturing TqSdk credentials at the terminal only.

    This is a capture BOUNDARY, not a login, and it never performs network or
    authentication work.  Any implementation MUST:
      - read credentials only from an interactive terminal (hidden input);
      - hold credentials in memory only (never persist, never log, never commit);
      - fail closed if either credential is empty.
    """

    def capture(self) -> tuple[str, str]: ...


class TerminalAuthCapture:
    """Runtime-only hidden terminal credential capture (in-memory only)."""

    def capture(self) -> tuple[str, str]:
        import getpass
        import sys

        if not sys.stdin.isatty():
            raise SourceGovernedMappingError(
                "terminal-only auth capture requires an interactive terminal; nothing captured"
            )
        account = input("TqSdk account (terminal only, hidden): ").strip()
        password = getpass.getpass("TqSdk password (terminal only, hidden): ")
        if not account or not password:
            raise SourceGovernedMappingError(
                "credentials are required at runtime; nothing was captured or persisted"
            )
        return account, password


TerminalCredentialsProvider = Callable[[], tuple[str, str]]
"""Runtime credentials provider type used to construct an authenticated session later."""


# ---------------------------------------------------------------------------
# TqSdk decode boundary (deliberately NOT implemented)
# ---------------------------------------------------------------------------


class TqSdkMappingDecodeBoundary(Protocol):
    """Boundary for a future Owner-authorized TqSdk decode adapter.

    NOT IMPLEMENTED: ``BLOCKED_API_CONTRACT_NOT_PINNED``.  The exact
    ``TqApi.query_his_cont_quotes`` response schema is not pinned by evidence,
    so no adapter may be written yet.  A future adapter (only under explicit
    Owner authorization and after the response contract is pinned) must:
      - bind exact source response bytes (``source_artifact_identity`` /
        ``exact_bytes_bound=True`` in ``MappingProvenance``);
      - preserve the source-defined next-trading-day switch;
      - produce ``SourceGovernedMappingRecord`` objects carrying the
        ``SOURCE_GOVERNED`` derivation marker.
    """

    def decode(self, payload: object) -> tuple[SourceGovernedMappingRecord, ...]: ...


__all__ = [
    "BLOCKED_API_CONTRACT_NOT_PINNED",
    "TQSDK_DECODE_NOT_IMPLEMENTED",
    "MappingProvenance",
    "MappingMembershipViolation",
    "MappingSubstitutionForbidden",
    "MappingUnavailableError",
    "MappingConflictError",
    "PseudoMainBarForbidden",
    "SourceGovernedMappingError",
    "SourceGovernedMappingRecord",
    "SourceGovernedMappingResolution",
    "SourceGovernedMappingSchedule",
    "TerminalAuthCapture",
    "TerminalCredentialsProvider",
    "TerminalOnlyAuthCapture",
    "TqSdkMappingDecodeBoundary",
    "assert_not_pseudo_main_target",
    "assert_source_governed_derivation",
]

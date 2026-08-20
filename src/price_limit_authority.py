"""Governed historical price-limit authority (fail-closed) for the canonical corpus.

This module reduces LIMIT-001 (HISTORICAL_PRICE_LIMIT_METADATA) for
`cu, al, ni, au, ag, rb` over `2024-01-01..2025-12-31` on SHFE by:

- binding the **contract-text base daily price limit** (涨跌停板幅度) per product with an
  explicit effective period, binding notice, source reference, retrieval timestamp and
  exact evidence classification (`BASE_CONTRACT_TEXT_BOUND`);
- recording the **special-day layers** (new-listing first day, resumption after
  suspension, consecutive same-direction limit, pre-holiday adjustment) as `UNKNOWN`
  unless a bound official rule text exists;
- recording the **per-day exchange-adjustment layer** as `HISTORICAL_GAP` for the window;
- providing a **fail-closed lookup interface**: a per-day operative limit is returned only
  when exactly one bound per-day fact exists; it is **never** derived from a base rule and
  **never** backfilled from a current rule.

Invariants enforced by construction and by tests:

1. ``resolve_per_day`` returns `BOUND` only from ``per_day_facts``; no code path applies
   ``base_limit_pct`` to a historical day.
2. ``require_per_day_fact`` raises unless exactly one bound per-day fact exists, so any
   execution-simulation claim of a *real* price-limit fill for a 2024-2025 day is rejected
   (fail closed) when the operative fact is not bound.
3. Every identity is a canonical content hash; changing any bound field changes the
   authority identity.

This prep binds the *rule authority* and the *interface*. Absolute per-day lower/upper
bounds additionally require the official previous-settlement price per concrete contract
per day, which is outside this rule-metadata prep and remains unbound for a future
governed step.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
import json
import re
from pathlib import Path
from typing import Iterable

from src.metadata_authority import canonical_hash

_SHA256 = re.compile(r"^[0-9a-f]{64}$")

PRICE_LIMIT_CLASSIFICATIONS = frozenset(
    {
        "BASE_CONTRACT_TEXT_BOUND",  # contract-text base limit, binding-notice chain + hashed official page
        "PER_DAY_ADJUSTMENT_BOUND",  # per-day exchange adjustment fact bound to an official notice
        "SPECIAL_DAY_RULE_BOUND",  # special-day rule bound to official rule text
        "HISTORICAL_GAP",  # no bound official value for the period
        "RETRIEVAL_BLOCKED",  # official source known but not retrievable this pass
        "UNKNOWN",  # not bound, not known
    }
)

# Retrieval/evidence status of a source artifact (mirrors E06 evidence_status_enum).
PRICE_LIMIT_SOURCE_STATUSES = frozenset(
    {
        "EXACT_OFFICIAL_BOUND",  # exact bytes of an official artifact bound by SHA256
        "REPOSITORY_VERIFIED_REFERENCE",  # committed repo evidence; no external byte hash claimed
        "OFFICIAL_REFERENCE_ONLY",  # official URL known; content not bound
        "RETRIEVAL_BLOCKED",  # official source known but not retrievable this pass
        "UNKNOWN",
    }
)

PER_DAY_STATUS_BOUND = "BOUND"
PER_DAY_STATUS_UNKNOWN = "UNKNOWN"
PER_DAY_STATUS_CONFLICT = "CONFLICT"


def _required_text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")


class PriceLimitAuthorityError(ValueError):
    """Raised when a required price-limit authority fact cannot be resolved."""


@dataclass(frozen=True)
class PriceLimitSource:
    """Binding metadata for one official price-limit source artifact (or explicit pending)."""

    source_id: str
    authority: str
    title: str
    source_url: str
    classification: str
    retrieved_at: datetime | None
    artifact_sha256: str | None = None
    products: tuple[str, ...] = ()
    content_notes: str = ""

    def __post_init__(self) -> None:
        for value, name in (
            (self.source_id, "price-limit source id"),
            (self.authority, "price-limit source authority"),
            (self.title, "price-limit source title"),
            (self.source_url, "price-limit source URL"),
            (self.classification, "price-limit source classification"),
        ):
            _required_text(value, name)
        if self.classification not in PRICE_LIMIT_SOURCE_STATUSES:
            raise ValueError("price-limit source classification is not recognized")
        if self.retrieved_at is not None and self.retrieved_at.tzinfo is None:
            raise ValueError("price-limit source retrieval timestamp must be timezone-aware")
        if self.artifact_sha256 is not None and not _SHA256.fullmatch(self.artifact_sha256):
            raise ValueError("price-limit source artifact SHA256 must be 64 lowercase hex characters")
        if self.classification == "EXACT_OFFICIAL_BOUND" and self.artifact_sha256 is None:
            raise ValueError("EXACT_OFFICIAL_BOUND price-limit source requires an artifact SHA256")
        if not isinstance(self.products, tuple):
            raise ValueError("price-limit source products must be a tuple")
        if not isinstance(self.content_notes, str):
            raise ValueError("price-limit source content notes must be a string")

    def identity(self) -> str:
        return canonical_hash(
            {
                "source_id": self.source_id,
                "authority": self.authority,
                "title": self.title,
                "source_url": self.source_url,
                "classification": self.classification,
                "retrieved_at": None if self.retrieved_at is None else self.retrieved_at.isoformat(),
                "artifact_sha256": self.artifact_sha256,
                "products": list(self.products),
                "content_notes": self.content_notes,
            }
        )


@dataclass(frozen=True)
class BasePriceLimitRule:
    """Contract-text base daily price-limit rule with an explicit effective period.

    This is the normal-day default clause (涨跌停板幅度) written into the SHFE contract
    text and anchored to an official binding notice. It is a *rule fact*, not a per-day
    operative fact: it must never be used alone to claim a per-day execution bound.
    """

    product: str
    trading_code: str
    base_limit_pct: Decimal
    limit_unit: str
    symmetric: bool
    basis: str
    binding_notice: str
    effective_start: date
    effective_end: date
    effective_period_proof: str
    classification: str
    source_references: tuple[str, ...] = ()
    in_window_delivery_grade_revisions_only: tuple[str, ...] = ()
    notes: str = ""

    def __post_init__(self) -> None:
        for value, name in (
            (self.product, "base price-limit product"),
            (self.trading_code, "base price-limit trading code"),
            (self.limit_unit, "base price-limit unit"),
            (self.basis, "base price-limit basis"),
            (self.binding_notice, "base price-limit binding notice"),
            (self.effective_period_proof, "base price-limit effective period proof"),
            (self.classification, "base price-limit classification"),
        ):
            _required_text(value, name)
        if type(self.base_limit_pct) is not Decimal or not self.base_limit_pct.is_finite() or self.base_limit_pct <= 0:
            raise ValueError("base limit percent must be a positive finite Decimal")
        if self.classification not in PRICE_LIMIT_CLASSIFICATIONS:
            raise ValueError("base price-limit classification is not recognized")
        if self.effective_end < self.effective_start:
            raise ValueError("base price-limit effective period end must follow its start")
        for value, name in (
            (self.source_references, "base price-limit source references"),
            (self.in_window_delivery_grade_revisions_only, "base price-limit in-window revisions"),
        ):
            if not isinstance(value, tuple):
                raise ValueError(f"{name} must be a tuple")
        if not isinstance(self.notes, str):
            raise ValueError("base price-limit notes must be a string")

    def covers(self, day: date) -> bool:
        return self.effective_start <= day <= self.effective_end

    def identity(self) -> str:
        return canonical_hash(
            {
                "product": self.product,
                "trading_code": self.trading_code,
                "base_limit_pct": str(self.base_limit_pct),
                "limit_unit": self.limit_unit,
                "symmetric": self.symmetric,
                "basis": self.basis,
                "binding_notice": self.binding_notice,
                "effective_start": self.effective_start.isoformat(),
                "effective_end": self.effective_end.isoformat(),
                "effective_period_proof": self.effective_period_proof,
                "classification": self.classification,
                "source_references": list(self.source_references),
                "in_window_delivery_grade_revisions_only": list(self.in_window_delivery_grade_revisions_only),
                "notes": self.notes,
            }
        )


@dataclass(frozen=True)
class PerDayLimitFact:
    """A bound per-day operative price-limit fact (limit percent for one product/day).

    Only such facts (never base rules) can satisfy a per-day lookup. ``adjustment_notice``
    names the official notice that establishes the operative value for that day.
    """

    fact_id: str
    product: str
    trading_day: date
    limit_pct: Decimal
    adjustment_notice: str
    classification: str
    source_references: tuple[str, ...] = ()
    notes: str = ""

    def __post_init__(self) -> None:
        for value, name in (
            (self.fact_id, "per-day price-limit fact id"),
            (self.product, "per-day price-limit product"),
            (self.adjustment_notice, "per-day price-limit adjustment notice"),
            (self.classification, "per-day price-limit classification"),
        ):
            _required_text(value, name)
        if type(self.limit_pct) is not Decimal or not self.limit_pct.is_finite() or self.limit_pct <= 0:
            raise ValueError("per-day limit percent must be a positive finite Decimal")
        if self.classification not in PRICE_LIMIT_CLASSIFICATIONS:
            raise ValueError("per-day price-limit classification is not recognized")
        if self.classification == "PER_DAY_ADJUSTMENT_BOUND" and not self.adjustment_notice.strip():
            raise ValueError("PER_DAY_ADJUSTMENT_BOUND requires a non-empty adjustment notice")
        if not isinstance(self.source_references, tuple):
            raise ValueError("per-day price-limit source references must be a tuple")

    def identity(self) -> str:
        return canonical_hash(
            {
                "fact_id": self.fact_id,
                "product": self.product,
                "trading_day": self.trading_day.isoformat(),
                "limit_pct": str(self.limit_pct),
                "adjustment_notice": self.adjustment_notice,
                "classification": self.classification,
                "source_references": list(self.source_references),
                "notes": self.notes,
            }
        )


@dataclass(frozen=True)
class PerDayLimitResolution:
    """Result of a per-day operative price-limit lookup (fail closed by design)."""

    status: str
    product: str
    trading_day: date
    per_day_fact: PerDayLimitFact | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        if self.status not in {PER_DAY_STATUS_BOUND, PER_DAY_STATUS_UNKNOWN, PER_DAY_STATUS_CONFLICT}:
            raise ValueError("per-day price-limit resolution status is not recognized")
        if not isinstance(self.product, str) or not self.product.strip():
            raise ValueError("per-day price-limit resolution product is required")
        if self.status == PER_DAY_STATUS_BOUND and self.per_day_fact is None:
            raise ValueError("BOUND per-day price-limit resolution requires a per-day fact")
        if self.status != PER_DAY_STATUS_BOUND and self.per_day_fact is not None:
            raise ValueError("non-BOUND per-day price-limit resolution must not carry a per-day fact")


class PriceLimitAuthority:
    """Fail-closed authority over base rules and bound per-day price-limit facts."""

    def __init__(
        self,
        *,
        schema_version: str,
        exchange: str,
        window_start: date,
        window_end: date,
        rules: Iterable[BasePriceLimitRule],
        per_day_facts: Iterable[PerDayLimitFact] = (),
        sources: Iterable[PriceLimitSource] = (),
    ) -> None:
        _required_text(schema_version, "price-limit authority schema version")
        _required_text(exchange, "price-limit authority exchange")
        if window_end < window_start:
            raise ValueError("price-limit authority window end must follow its start")
        self._schema_version = schema_version
        self._exchange = exchange
        self._window_start = window_start
        self._window_end = window_end
        self._rules = tuple(sorted(rules, key=lambda item: (item.product, item.effective_start, item.base_limit_pct)))
        self._per_day_facts = tuple(
            sorted(per_day_facts, key=lambda item: (item.product, item.trading_day, item.fact_id))
        )
        self._sources = {source.source_id: source for source in sources}
        self._validate()

    def _validate(self) -> None:
        for rule in self._rules:
            if rule.product not in self._rules_by_product():
                raise PriceLimitAuthorityError("price-limit authority rules must be complete per product")
        for fact in self._per_day_facts:
            if fact.product not in self._rules_by_product():
                raise PriceLimitAuthorityError("per-day price-limit fact references an ungoverned product")
            if not (self._window_start <= fact.trading_day <= self._window_end):
                raise PriceLimitAuthorityError("per-day price-limit fact must fall inside the authority window")
        for reference in self._all_source_references():
            if reference not in self._sources:
                raise PriceLimitAuthorityError(f"price-limit authority references unknown source {reference}")

    def _rules_by_product(self) -> dict[str, tuple[BasePriceLimitRule, ...]]:
        grouped: dict[str, list[BasePriceLimitRule]] = {}
        for rule in self._rules:
            grouped.setdefault(rule.product, []).append(rule)
        return {product: tuple(rules) for product, rules in grouped.items()}

    def _all_source_references(self) -> set[str]:
        references: set[str] = set()
        for rule in self._rules:
            references.update(rule.source_references)
        for fact in self._per_day_facts:
            references.update(fact.source_references)
        return references

    @property
    def schema_version(self) -> str:
        return self._schema_version

    @property
    def exchange(self) -> str:
        return self._exchange

    @property
    def window_start(self) -> date:
        return self._window_start

    @property
    def window_end(self) -> date:
        return self._window_end

    @property
    def products(self) -> tuple[str, ...]:
        return tuple(sorted(self._rules_by_product()))

    @property
    def per_day_fact_count(self) -> int:
        return len(self._per_day_facts)

    def covers(self, product: str, day: date) -> bool:
        """True when the authority window covers the product/day."""
        return product in self._rules_by_product() and self._window_start <= day <= self._window_end

    def base_rule(self, product: str, day: date) -> BasePriceLimitRule:
        """Resolve the single effective base rule for a product/day (fail closed).

        Raises :class:`PriceLimitAuthorityError` when no effective period covers the day
        or multiple non-identical rules conflict.
        """
        matching = [rule for rule in self._rules if rule.product == product and rule.covers(day)]
        if not matching:
            raise PriceLimitAuthorityError(
                f"no base price-limit rule effective period covers {product} on {day.isoformat()}"
            )
        distinct = {rule.identity() for rule in matching}
        if len(distinct) > 1:
            raise PriceLimitAuthorityError(
                f"conflicting base price-limit rules cover {product} on {day.isoformat()}"
            )
        return matching[0]

    def per_day_resolution(self, product: str, day: date) -> PerDayLimitResolution:
        """Resolve the bound per-day operative price-limit fact (fail closed by design).

        Returns ``BOUND`` only when exactly one bound per-day fact exists for the
        product/day. Never derives a fact from a base rule and never backfills a current
        rule onto a historical day.
        """
        matching = [fact for fact in self._per_day_facts if fact.product == product and fact.trading_day == day]
        if not matching:
            return PerDayLimitResolution(
                PER_DAY_STATUS_UNKNOWN,
                product,
                day,
                None,
                f"no bound per-day price-limit fact for {product} on {day.isoformat()} "
                "(per-day adjustment layer is HISTORICAL_GAP / UNKNOWN)",
            )
        distinct = {fact.identity() for fact in matching}
        if len(distinct) > 1:
            return PerDayLimitResolution(
                PER_DAY_STATUS_CONFLICT,
                product,
                day,
                None,
                f"conflicting bound per-day price-limit facts cover {product} on {day.isoformat()}",
            )
        return PerDayLimitResolution(PER_DAY_STATUS_BOUND, product, day, matching[0], None)

    def per_day_classification(self, product: str, day: date) -> str:
        """Exact evidence classification for the per-day operative fact on product/day."""
        resolution = self.per_day_resolution(product, day)
        if resolution.status == PER_DAY_STATUS_BOUND:
            return resolution.per_day_fact.classification
        if resolution.status == PER_DAY_STATUS_CONFLICT:
            return "CONFLICT"
        return "UNKNOWN"

    def require_per_day_fact(self, product: str, day: date) -> PerDayLimitFact:
        """Deterministic fail-closed gate for a per-day operative price-limit fact.

        Raises :class:`PriceLimitAuthorityError` unless exactly one bound per-day fact
        exists. Execution simulation that claims a *real* price-limit fill must obtain a
        fact through this gate; with none bound, the claim is rejected.
        """
        resolution = self.per_day_resolution(product, day)
        if resolution.status != PER_DAY_STATUS_BOUND:
            raise PriceLimitAuthorityError(
                f"price-limit fact required for {product} on {day.isoformat()} is fail-closed: {resolution.reason}"
            )
        return resolution.per_day_fact

    def authority_identity(self) -> str:
        """Canonical content identity of the whole authority."""
        return canonical_hash(
            {
                "schema_version": self._schema_version,
                "exchange": self._exchange,
                "window_start": self._window_start.isoformat(),
                "window_end": self._window_end.isoformat(),
                "rules": [rule.identity() for rule in self._rules],
                "per_day_facts": [fact.identity() for fact in self._per_day_facts],
                "sources": sorted(source.identity() for source in self._sources.values()),
            }
        )

    @classmethod
    def from_evidence_json(cls, path: str | Path) -> "PriceLimitAuthority":
        """Load the authority from the committed machine-readable evidence JSON."""
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        if raw.get("schema_version") != "historical-price-limit-authority-v0_1":
            raise PriceLimitAuthorityError("unrecognized price-limit authority schema version")

        sources: list[PriceLimitSource] = []
        for item in raw.get("sources", []):
            sources.append(
                PriceLimitSource(
                    source_id=item["source_id"],
                    authority=item.get("authority", ""),
                    title=item.get("title", ""),
                    source_url=item.get("source_url", ""),
                    classification=item.get("classification", "UNKNOWN"),
                    retrieved_at=(
                        None
                        if item.get("retrieved_at") is None
                        else datetime.fromisoformat(item["retrieved_at"])
                    ),
                    artifact_sha256=item.get("sha256"),
                    products=tuple(item.get("products", ())),
                    content_notes=item.get("content_notes", ""),
                )
            )

        rules: list[BasePriceLimitRule] = []
        for product, item in raw.get("product_rules", {}).items():
            rules.append(
                BasePriceLimitRule(
                    product=product,
                    trading_code=item["trading_code"],
                    base_limit_pct=Decimal(item["base_limit_pct"]),
                    limit_unit=item["limit_unit"],
                    symmetric=bool(item["symmetric"]),
                    basis=item["basis"],
                    binding_notice=item["binding_notice"],
                    effective_start=date.fromisoformat(item["effective_start"]),
                    effective_end=date.fromisoformat(item["effective_end"]),
                    effective_period_proof=item["effective_period_proof"],
                    classification=item["classification"],
                    source_references=tuple(item.get("source_references", ())),
                    in_window_delivery_grade_revisions_only=tuple(
                        item.get("in_window_delivery_grade_revisions_only", ())
                    ),
                    notes=item.get("notes", ""),
                )
            )

        per_day_facts: list[PerDayLimitFact] = []
        for item in raw.get("per_day_facts", []):
            per_day_facts.append(
                PerDayLimitFact(
                    fact_id=item["fact_id"],
                    product=item["product"],
                    trading_day=date.fromisoformat(item["trading_day"]),
                    limit_pct=Decimal(item["limit_pct"]),
                    adjustment_notice=item["adjustment_notice"],
                    classification=item["classification"],
                    source_references=tuple(item.get("source_references", ())),
                    notes=item.get("notes", ""),
                )
            )

        window = raw["window"]
        authority = cls(
            schema_version=raw["schema_version"],
            exchange=raw["exchange"],
            window_start=date.fromisoformat(window["start"]),
            window_end=date.fromisoformat(window["end"]),
            rules=rules,
            per_day_facts=per_day_facts,
            sources=sources,
        )

        recorded_identity = raw.get("identity")
        if isinstance(recorded_identity, str) and _SHA256.fullmatch(recorded_identity):
            computed = authority.authority_identity()
            if recorded_identity != computed:
                raise PriceLimitAuthorityError(
                    "price-limit authority identity mismatch between recorded and computed content"
                )
        return authority

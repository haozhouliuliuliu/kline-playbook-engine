"""Immutable canonical corpus identity for the BALANCED research dataset.

Binds, as one deterministic identity, every material fact of the accepted
canonical corpus:

- approved source identity (provider + adapter/source identity);
- exact product universe;
- exact date coverage;
- concrete-contract inventory rule identity;
- raw artifact manifest root identity;
- governed metadata root identity;
- normalizer/schema identity;
- Parquet schema/storage version;
- accepted partition identities;
- quality / cross-source summary.

Building/acquiring the corpus does NOT expose it to any strategy lineage; no
development/validation/final-unseen split is created here.  This module
contains no credentials and no raw market data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from hashlib import sha256
import json
from typing import Iterable


def canonical_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _required_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")


@dataclass(frozen=True)
class CanonicalCorpusIdentity:
    schema_version: str
    source_provider: str
    source_identity_id: str
    products: tuple[str, ...]
    coverage_start: date
    coverage_end: date
    inventory_rule_identity: str
    raw_manifest_root_identity: str
    governed_metadata_root_identity: str
    normalizer_identity: str
    parquet_schema_version: str
    parquet_storage_version: str
    partition_identities: tuple[str, ...]
    quality_summary_identity: str
    cross_source_summary_identity: str

    def __post_init__(self) -> None:
        for value, name in (
            (self.schema_version, "canonical corpus schema version"),
            (self.source_provider, "canonical corpus source provider"),
            (self.source_identity_id, "canonical corpus source identity"),
            (self.inventory_rule_identity, "canonical corpus inventory rule identity"),
            (self.raw_manifest_root_identity, "canonical corpus raw manifest root identity"),
            (self.governed_metadata_root_identity, "canonical corpus governed metadata root identity"),
            (self.normalizer_identity, "canonical corpus normalizer identity"),
            (self.parquet_schema_version, "canonical corpus parquet schema version"),
            (self.parquet_storage_version, "canonical corpus parquet storage version"),
            (self.quality_summary_identity, "canonical corpus quality summary identity"),
            (self.cross_source_summary_identity, "canonical corpus cross-source summary identity"),
        ):
            _required_text(value, name)
        if not self.products:
            raise ValueError("canonical corpus requires at least one product")
        if not self.partition_identities:
            raise ValueError("canonical corpus requires at least one accepted partition identity")
        if self.coverage_end < self.coverage_start:
            raise ValueError("canonical corpus coverage end must follow its start")
        if len(set(self.products)) != len(self.products):
            raise ValueError("canonical corpus products must be unique")

    def identity_id(self) -> str:
        return canonical_hash(
            {
                "schema_version": self.schema_version,
                "source_provider": self.source_provider,
                "source_identity_id": self.source_identity_id,
                "products": sorted(self.products),
                "coverage_start": self.coverage_start.isoformat(),
                "coverage_end": self.coverage_end.isoformat(),
                "inventory_rule_identity": self.inventory_rule_identity,
                "raw_manifest_root_identity": self.raw_manifest_root_identity,
                "governed_metadata_root_identity": self.governed_metadata_root_identity,
                "normalizer_identity": self.normalizer_identity,
                "parquet_schema_version": self.parquet_schema_version,
                "parquet_storage_version": self.parquet_storage_version,
                "partition_identities": sorted(self.partition_identities),
                "quality_summary_identity": self.quality_summary_identity,
                "cross_source_summary_identity": self.cross_source_summary_identity,
            }
        )

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "canonical_corpus_identity": self.identity_id(),
            "source_provider": self.source_provider,
            "source_identity_id": self.source_identity_id,
            "products": sorted(self.products),
            "coverage_start": self.coverage_start.isoformat(),
            "coverage_end": self.coverage_end.isoformat(),
            "inventory_rule_identity": self.inventory_rule_identity,
            "raw_manifest_root_identity": self.raw_manifest_root_identity,
            "governed_metadata_root_identity": self.governed_metadata_root_identity,
            "normalizer_identity": self.normalizer_identity,
            "parquet_schema_version": self.parquet_schema_version,
            "parquet_storage_version": self.parquet_storage_version,
            "partition_identities": sorted(self.partition_identities),
            "quality_summary_identity": self.quality_summary_identity,
            "cross_source_summary_identity": self.cross_source_summary_identity,
        }


def governed_metadata_root_identity(
    calendar_identity: str,
    spec_identities: Iterable[str],
    schedule_identities: Iterable[str],
    universe_identities: Iterable[str],
    metadata_schema_version: str,
) -> str:
    """Deterministic root identity over the governed metadata authority facts."""
    return canonical_hash(
        {
            "schema_version": metadata_schema_version,
            "trading_calendar_identity": calendar_identity,
            "contract_spec_identities": sorted(set(spec_identities)),
            "session_schedule_identities": sorted(set(schedule_identities)),
            "contract_universe_identities": sorted(set(universe_identities)),
        }
    )

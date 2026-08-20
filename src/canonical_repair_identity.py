"""Deterministic identity for a REPAIRED canonical candidate corpus.

A repaired candidate corpus is a fully independent assembly produced by
``tools/build_repaired_canonical_candidate.py`` after every D01/D02
replacement partition has been qualified (116/116 REPAIRED_PASS, no residual
D01/D02/drift/authority-mismatch).  It inherits 32,864 already-PASS accepted
partitions as-is and replaces 116 partitions with qualified replacement raw.

This identity exists to make the repaired candidate corpus unambiguous:

- it MUST be a NEW identity, never the accepted corpus identity
  (``1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8``);
- it MUST preserve the parent/historical lineage (parent corpus identity +
  parent raw-manifest root identity + the qualification evidence identity);
- it MUST NOT claim a re-verified cross-source summary: the repaired candidate
  has NOT been cross-source verified, so ``cross_source_summary_identity`` is
  the explicit sentinel ``CANDIDATE_NOT_REVERIFIED`` rather than the accepted
  corpus's cross-source identity.

This module contains no credentials, no raw market data, and no candidate
outcome.  It never rewrites ``CANONICAL_DATASET_ACCEPTANCE`` or any accepted
corpus artifact.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from src.canonical_identity import canonical_hash

# Accepted corpus lineage facts (immutable acceptance evidence, recorded in
# docs/evidence/CANONICAL_CORPUS_IDENTITY.json and
# docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md).
PARENT_CANONICAL_CORPUS_IDENTITY = (
    "1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8"
)
PARENT_RAW_MANIFEST_ROOT_IDENTITY = (
    "7510a4a943e85c9be256e62971b5a64d64e9976c2b01c9f5d0fe07b1c6c8d324"
)

# The repaired candidate has not been cross-source verified; binding the
# accepted corpus's cross-source identity here would be a false claim.
CROSS_SOURCE_CANDIDATE_NOT_REVERIFIED = "CANDIDATE_NOT_REVERIFIED"


def _required_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")


@dataclass(frozen=True)
class RepairedCandidateCorpusIdentity:
    """One deterministic identity over every material fact of the repaired
    candidate corpus, including the parent/historical lineage.

    The identity value is content-derived: identical inputs always yield the
    identical ``identity_id``, and any change in the assembled partitions,
    lineage, or qualification evidence changes the identity.
    """

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
    parent_canonical_corpus_identity: str
    parent_raw_manifest_root_identity: str
    qualification_evidence_identity: str
    repaired_target_count: int
    inherited_partition_count: int

    def __post_init__(self) -> None:
        for value, name in (
            (self.schema_version, "repaired candidate identity schema version"),
            (self.source_provider, "repaired candidate source provider"),
            (self.source_identity_id, "repaired candidate source identity"),
            (self.inventory_rule_identity, "repaired candidate inventory rule identity"),
            (self.raw_manifest_root_identity, "repaired candidate raw manifest root identity"),
            (self.governed_metadata_root_identity, "repaired candidate governed metadata root identity"),
            (self.normalizer_identity, "repaired candidate normalizer identity"),
            (self.parquet_schema_version, "repaired candidate parquet schema version"),
            (self.parquet_storage_version, "repaired candidate parquet storage version"),
            (self.quality_summary_identity, "repaired candidate quality summary identity"),
            (self.cross_source_summary_identity, "repaired candidate cross-source summary identity"),
            (self.parent_canonical_corpus_identity, "parent canonical corpus identity"),
            (self.parent_raw_manifest_root_identity, "parent raw manifest root identity"),
            (self.qualification_evidence_identity, "qualification evidence identity"),
        ):
            _required_text(value, name)
        if not self.products:
            raise ValueError("repaired candidate identity requires at least one product")
        if not self.partition_identities:
            raise ValueError("repaired candidate identity requires at least one partition identity")
        if self.coverage_end < self.coverage_start:
            raise ValueError("repaired candidate coverage end must follow its start")
        if len(set(self.products)) != len(self.products):
            raise ValueError("repaired candidate products must be unique")
        if self.repaired_target_count < 0 or self.inherited_partition_count < 0:
            raise ValueError("repaired candidate partition counts must be non-negative")
        if self.parent_canonical_corpus_identity == self.identity_id():
            raise ValueError("repaired candidate identity must differ from its parent identity")
        # A candidate must never claim an accepted cross-source summary.
        if self.cross_source_summary_identity == "CANDIDATE_NOT_REVERIFIED":
            return
        raise ValueError(
            "repaired candidate cross-source summary must be the "
            "CANDIDATE_NOT_REVERIFIED sentinel until independently re-verified"
        )

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
                "parent_canonical_corpus_identity": self.parent_canonical_corpus_identity,
                "parent_raw_manifest_root_identity": self.parent_raw_manifest_root_identity,
                "qualification_evidence_identity": self.qualification_evidence_identity,
                "repaired_target_count": self.repaired_target_count,
                "inherited_partition_count": self.inherited_partition_count,
            }
        )

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "repaired_candidate_identity": self.identity_id(),
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
            "parent_canonical_corpus_identity": self.parent_canonical_corpus_identity,
            "parent_raw_manifest_root_identity": self.parent_raw_manifest_root_identity,
            "qualification_evidence_identity": self.qualification_evidence_identity,
            "repaired_target_count": self.repaired_target_count,
            "inherited_partition_count": self.inherited_partition_count,
            "candidate_status": "CANDIDATE",
        }


def qualification_evidence_identity(
    schema_version: str,
    target_partition_count: int,
    totals: dict,
    diagnostics: Iterable[dict],
) -> str:
    """Deterministic identity over the material qualification-evidence facts.

    Deliberately excludes machine-dependent fields (e.g. ``candidate_raw_path``
    absolute paths) so the identity is reproducible across machines and
    worktrees.  It binds the evidence schema, target count, totals, and the
    per-partition qualification outcome facts.
    """
    normalized = []
    for diagnostic in sorted(diagnostics, key=lambda item: str(item.get("partition_identity"))):
        normalized.append(
            {
                "partition_identity": diagnostic.get("partition_identity"),
                "qualification_status": diagnostic.get("qualification_status"),
                "contract": diagnostic.get("contract"),
                "trading_day": diagnostic.get("trading_day"),
                "requested_start": diagnostic.get("requested_start"),
                "requested_end": diagnostic.get("requested_end"),
                "candidate_returned_start": diagnostic.get("candidate_returned_start"),
                "candidate_returned_end": diagnostic.get("candidate_returned_end"),
                "truncation_shape": diagnostic.get("truncation_shape"),
                "missing_region_shape": diagnostic.get("missing_region_shape"),
                "missing_expected_bar_count": diagnostic.get("missing_expected_bar_count"),
                "authority_boundary_reasons": diagnostic.get("authority_boundary_reasons", []),
                "historical_provider_value_drift": diagnostic.get(
                    "historical_provider_value_drift", False
                ),
            }
        )
    return canonical_hash(
        {
            "schema_version": schema_version,
            "target_partition_count": target_partition_count,
            "totals": totals,
            "diagnostics": normalized,
        }
    )

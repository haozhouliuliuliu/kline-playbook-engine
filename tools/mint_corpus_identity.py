"""Mint the immutable canonical corpus identity for the accepted BALANCED corpus.

Deterministically binds every material fact of the accepted canonical dataset
into one identity: approved source, product universe, coverage, concrete-
contract inventory rule, raw manifest root, governed metadata root, normalizer,
Parquet schema/storage versions, accepted partition identities, quality
summary, and cross-source summary.

Reads ONLY committed evidence + the accepted manifest (no credentials, no raw
market data).  The identity is reproducible from the committed evidence alone.

Usage (pyarrow venv):
  python -m tools.mint_corpus_identity
"""
from __future__ import annotations

import json
from pathlib import Path

from src.canonical_identity import (
    CanonicalCorpusIdentity,
    governed_metadata_root_identity,
    canonical_hash,
)
from src.canonical_storage import (
    CANONICAL_SCHEMA_VERSION,
    PARQUET_STORAGE_VERSION,
)
from src.historical_manifest import DatasetManifest
from tools.build_canonical_dataset import (
    COVERAGE_END,
    COVERAGE_START,
    INVENTORY_RULE_IDENTITY,
    PRODUCTS,
    PROJECT_ROOT,
    SOURCE_SPEC,
    load_calendar,
    load_schedules,
    load_specs,
    load_universe,
)

EVIDENCE = PROJECT_ROOT / "docs" / "evidence"
MANIFEST = PROJECT_ROOT / "data" / "canonical" / "manifest.json"
CROSS_SOURCE = EVIDENCE / "CANONICAL_FULL_CROSS_SOURCE.json"
METADATA_SCHEMA_VERSION = "canonical-governed-metadata-v1"
IDENTITY_SCHEMA_VERSION = "canonical-corpus-identity-v1"
OUT = EVIDENCE / "CANONICAL_CORPUS_IDENTITY.json"


def _load_json(path: Path) -> dict:
    data = json.loads(path.read_bytes().decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} is not a JSON object")
    return data


def _source_identity_id() -> str:
    """Deterministic identity over the immutable source specification facts."""
    return canonical_hash(
        {
            "provider": SOURCE_SPEC.provider,
            "source_type": SOURCE_SPEC.source_type,
            "endpoint_identity": SOURCE_SPEC.endpoint_identity,
            "raw_schema_identity": SOURCE_SPEC.raw_schema_identity,
            "provider_dataset_version": SOURCE_SPEC.provider_dataset_version,
            "normalizer_identity": SOURCE_SPEC.normalizer.identity_id,
            "availability_rule": SOURCE_SPEC.availability_rule,
        }
    )


def main() -> None:
    calendar = load_calendar()
    specs = load_specs()
    schedules = load_schedules()
    universe = load_universe()
    manifest = DatasetManifest.load(MANIFEST)

    universe_data = _load_json(EVIDENCE / "CANONICAL_CONTRACT_UNIVERSE.json")
    universe_identities = sorted(
        canonical_hash(entry) for entry in universe_data["contracts"]
    )

    metadata_root = governed_metadata_root_identity(
        calendar_identity=calendar.identity(),
        spec_identities=[s.identity() for s in specs.values()],
        schedule_identities=[s.identity() for s in schedules.values()],
        universe_identities=universe_identities,
        metadata_schema_version=METADATA_SCHEMA_VERSION,
    )

    partition_identities = sorted(p.identity() for p in manifest.partitions)

    quality_counts: dict[str, int] = {}
    for p in manifest.partitions:
        quality_counts[p.quality_status] = quality_counts.get(p.quality_status, 0) + 1
    quality_summary = {
        "total_partitions": len(manifest.partitions),
        "by_status": dict(sorted(quality_counts.items())),
        "all_accepted": all(p.quality_status == "PASS" for p in manifest.partitions),
    }
    quality_summary_identity = canonical_hash(quality_summary)

    cross = _load_json(CROSS_SOURCE)
    cross_source_summary_identity = cross["summary"]["summary_identity"]

    source_identity_id = _source_identity_id()
    identity = CanonicalCorpusIdentity(
        schema_version=IDENTITY_SCHEMA_VERSION,
        source_provider=SOURCE_SPEC.provider,
        source_identity_id=source_identity_id,
        products=tuple(PRODUCTS),
        coverage_start=COVERAGE_START,
        coverage_end=COVERAGE_END,
        inventory_rule_identity=INVENTORY_RULE_IDENTITY,
        raw_manifest_root_identity=manifest.identity(),
        governed_metadata_root_identity=metadata_root,
        normalizer_identity=SOURCE_SPEC.normalizer.identity_id,
        parquet_schema_version=CANONICAL_SCHEMA_VERSION,
        parquet_storage_version=PARQUET_STORAGE_VERSION,
        partition_identities=partition_identities,
        quality_summary_identity=quality_summary_identity,
        cross_source_summary_identity=cross_source_summary_identity,
    )

    record = {
        "schema_version": IDENTITY_SCHEMA_VERSION,
        "canonical_corpus_identity": identity.identity_id(),
        "source_provider": SOURCE_SPEC.provider,
        "source_identity_id": source_identity_id,
        "products": sorted(PRODUCTS),
        "coverage_start": COVERAGE_START.isoformat(),
        "coverage_end": COVERAGE_END.isoformat(),
        "inventory_rule_identity": INVENTORY_RULE_IDENTITY,
        "raw_manifest_root_identity": manifest.identity(),
        "governed_metadata_root_identity": metadata_root,
        "governed_metadata_schema_version": METADATA_SCHEMA_VERSION,
        "normalizer_identity": SOURCE_SPEC.normalizer.identity_id,
        "parquet_schema_version": CANONICAL_SCHEMA_VERSION,
        "parquet_storage_version": PARQUET_STORAGE_VERSION,
        "partition_count": len(partition_identities),
        "partition_identity_count": len(set(partition_identities)),
        "quality_summary": quality_summary,
        "quality_summary_identity": quality_summary_identity,
        "cross_source_summary": cross["summary"],
        "cross_source_summary_identity": cross_source_summary_identity,
        "evidence_references": {
            "manifest": "data/canonical/manifest.json",
            "governed_metadata": [
                "CANONICAL_TRADING_CALENDAR.json",
                "CANONICAL_CONTRACT_SPECS.json",
                "CANONICAL_SESSION_SCHEDULES.json",
                "CANONICAL_CONTRACT_UNIVERSE.json",
            ],
            "cross_source": "CANONICAL_FULL_CROSS_SOURCE.json",
        },
    }

    OUT.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "canonical_corpus_identity": identity.identity_id(),
                "partition_count": len(partition_identities),
                "unique_partition_identities": len(set(partition_identities)),
                "quality_summary_identity": quality_summary_identity,
                "cross_source_summary_identity": cross_source_summary_identity,
                "wrote": str(OUT),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

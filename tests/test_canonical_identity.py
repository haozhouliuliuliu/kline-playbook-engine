"""Tests for canonical corpus identity (immutable binding)."""

from __future__ import annotations

import unittest
from datetime import date

from src.canonical_identity import CanonicalCorpusIdentity, governed_metadata_root_identity


def _identity(partitions=("p1", "p2")) -> CanonicalCorpusIdentity:
    return CanonicalCorpusIdentity(
        schema_version="canonical-corpus-identity-v1",
        source_provider="TQSDK",
        source_identity_id="src1",
        products=("cu", "al", "ni", "au", "ag", "rb"),
        coverage_start=date(2024, 1, 1),
        coverage_end=date(2025, 12, 31),
        inventory_rule_identity="pit-complete-listed-concrete-contract-universe-v1",
        raw_manifest_root_identity="manifest1",
        governed_metadata_root_identity="meta1",
        normalizer_identity="norm1",
        parquet_schema_version="canonical-normalized-bar-v1",
        parquet_storage_version="parquet-partitioned-v1",
        partition_identities=partitions,
        quality_summary_identity="q1",
        cross_source_summary_identity="x1",
    )


class CanonicalCorpusIdentityTests(unittest.TestCase):
    def test_identity_is_deterministic(self) -> None:
        self.assertEqual(_identity().identity_id(), _identity().identity_id())

    def test_partition_order_insensitive(self) -> None:
        a = _identity(partitions=("p1", "p2"))
        b = _identity(partitions=("p2", "p1"))
        self.assertEqual(a.identity_id(), b.identity_id())

    def test_material_change_changes_identity(self) -> None:
        a = _identity()
        b = _identity(partitions=("p1", "p3"))
        self.assertNotEqual(a.identity_id(), b.identity_id())

    def test_empty_partitions_fail(self) -> None:
        with self.assertRaises(ValueError):
            _identity(partitions=())

    def test_to_dict_round_trip(self) -> None:
        d = _identity().to_dict()
        self.assertEqual(d["canonical_corpus_identity"], _identity().identity_id())

    def test_governed_metadata_root_identity(self) -> None:
        root = governed_metadata_root_identity(
            "cal", ["s1", "s2"], ["sched"], ["u1", "u2"], "meta-schema-v1"
        )
        root2 = governed_metadata_root_identity(
            "cal", ["s2", "s1"], ["sched"], ["u2", "u1"], "meta-schema-v1"
        )
        self.assertEqual(root, root2)
        self.assertEqual(len(root), 64)


if __name__ == "__main__":
    unittest.main()

"""Tests for canonical normalized storage (Parquet + SQLite catalog).

Parquet round-trip tests require the pinned canonical-build pyarrow runtime
(tested version 25.0.1) and are skipped in the stdlib-only environment; they
run under the isolated pyarrow venv.  SQLite catalog tests always run.
"""

from __future__ import annotations

import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from src.canonical_storage import (
    CANONICAL_SCHEMA_VERSION,
    PARQUET_STORAGE_VERSION,
    SQLITE_CATALOG_SCHEMA_VERSION,
    CanonicalCatalog,
    CanonicalRow,
    CatalogPartitionEntry,
    write_partition_table,
    read_partition_table,
    verify_round_trip,
)

try:
    import pyarrow  # noqa: F401

    HAVE_PYARROW = True
except Exception:  # noqa: BLE001 - stdlib-only environment
    HAVE_PYARROW = False

CN = ZoneInfo("Asia/Shanghai")


def _row(i: int) -> CanonicalRow:
    from decimal import Decimal

    return CanonicalRow(
        provider="TQSDK",
        source_type="PROFESSIONAL_HISTORICAL_API",
        exchange="SHFE",
        concrete_contract="SHFE.au2508",
        product="au",
        trading_day=date(2025, 6, 18),
        bar_start=datetime(2025, 6, 18, 9, 0 + i, tzinfo=CN),
        bar_end=datetime(2025, 6, 18, 9, 1 + i, tzinfo=CN),
        historical_available_at=datetime(2025, 6, 18, 9, 1 + i, tzinfo=CN),
        open=Decimal("786.26"),
        high=Decimal("787.50"),
        low=Decimal("785.90"),
        close=Decimal("786.88"),
        volume=100 + i,
        open_interest_start=10 + i,
        open_interest_end=11 + i,
        raw_artifact_identity_id="raw1",
        source_identity_id="src1",
        data_version_id="dv1",
        contract_metadata_identity="cm1",
        session_metadata_identity="sm1",
        normalizer_identity="norm1",
    )


@unittest.skipUnless(HAVE_PYARROW, "pyarrow not available in this environment")
class ParquetStorageTests(unittest.TestCase):
    def test_write_read_logical_equality(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "parquet"
            facts = write_partition_table(root, [_row(0), _row(1)])
            self.assertEqual(facts["row_count"], 2)
            self.assertGreater(facts["file_count"], 0)
            self.assertEqual(facts["storage_version"], PARQUET_STORAGE_VERSION)
            self.assertEqual(facts["schema_version"], CANONICAL_SCHEMA_VERSION)
            self.assertEqual(len(facts["logical_table_identity"]), 64)
            for f in facts["files"]:
                self.assertEqual(len(f["sha256"]), 64)
            self.assertTrue(verify_round_trip(root, [_row(0).to_pylist_row(), _row(1).to_pylist_row()]))

    def test_decimal_and_timezone_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "parquet"
            write_partition_table(root, [_row(0)])
            table = read_partition_table(root)
            self.assertEqual(table.schema.field("bar_start").type.tz, "Asia/Shanghai")
            self.assertEqual(str(table.column("close").to_pylist()[0]), "786.8800")
            self.assertEqual(table.column("trading_day").to_pylist(), [date(2025, 6, 18)])

    def test_empty_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                write_partition_table(Path(tmp) / "parquet", [])


class CanonicalCatalogTests(unittest.TestCase):
    def _entry(self) -> CatalogPartitionEntry:
        return CatalogPartitionEntry(
            provider="TQSDK",
            contract="SHFE.au2508",
            exchange="SHFE",
            granularity_seconds=60,
            trading_day=date(2025, 6, 18),
            raw_sha256="a" * 64,
            request_identity="req1",
            data_version_id="dv1",
            normalized_batch_id="nb1",
            parquet_artifact_identity="pa1",
            parquet_logical_identity="pl1",
            parquet_storage_version=PARQUET_STORAGE_VERSION,
            row_count=465,
            coverage_start="2025-06-17T21:00:00+08:00",
            coverage_end="2025-06-18T15:00:00+08:00",
            quality_status="PASS",
        )

    def test_catalog_upsert_query_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            catalog = CanonicalCatalog(Path(tmp) / "cat.sqlite")
            try:
                catalog.set_meta("schema_version", SQLITE_CATALOG_SCHEMA_VERSION)
                catalog.upsert_partition(self._entry())
                self.assertEqual(catalog.partition_count(), 1)
                self.assertEqual(catalog.row_count_total(), 465)
                rows = catalog.query(product="au")
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["contract"], "SHFE.au2508")
                self.assertEqual(len(catalog.identity()), 64)
            finally:
                catalog.close()

    def test_catalog_deterministic_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            a = CanonicalCatalog(Path(tmp) / "a.sqlite")
            b = CanonicalCatalog(Path(tmp) / "b.sqlite")
            try:
                a.upsert_partition(self._entry())
                b.upsert_partition(self._entry())
                self.assertEqual(a.identity(), b.identity())
            finally:
                a.close()
                b.close()

    def test_rebuild_replaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            catalog = CanonicalCatalog(Path(tmp) / "cat.sqlite")
            try:
                catalog.upsert_partition(self._entry())
                catalog.upsert_partition(self._entry())  # same key -> replace
                self.assertEqual(catalog.partition_count(), 1)
            finally:
                catalog.close()


if __name__ == "__main__":
    unittest.main()

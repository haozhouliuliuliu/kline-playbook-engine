"""Canonical normalized storage for the BALANCED research corpus.

Roles:
- NORMALIZED_BAR_STORAGE: deterministic partitioned Parquet layout
  ``exchange/product/contract/year/month`` with a fixed canonical schema that
  preserves Decimal/price semantics, timezone-aware timestamps, volume/OI, the
  concrete contract, the trading day, ``available_at`` and provenance identity
  links.  PyArrow is imported lazily so the stdlib verification path does not
  depend on it; the tested PyArrow capability/version is pinned by the
  project's canonical-build dependency mechanism (evidence:
  ``PYARROW_STATUS=ADOPTED``, tested version 25.0.1).
- MANIFEST/METADATA: a rebuildable SQLite catalog (stdlib ``sqlite3``) that
  indexes accepted partitions.  SQLite is NOT the historical truth authority:
  committed immutable manifests/evidence remain the durable provenance
  authority, and the catalog can be rebuilt from accepted manifests + parquet
  inventory.

Safety:
- no silent price rounding (Decimal columns are exact);
- no forward-fill / synthetic bars (only bars present in the accepted
  normalized batch are written);
- write/read logical equality is verified by casting the reconstructed table
  back to the canonical schema (partition columns come back dictionary-encoded
  and are restored deterministically).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
import json
import os
import sqlite3
from pathlib import Path
from typing import Iterable
from zoneinfo import ZoneInfo

CANONICAL_SCHEMA_VERSION = "canonical-normalized-bar-v1"
PARQUET_STORAGE_VERSION = "parquet-partitioned-v1"
SQLITE_CATALOG_SCHEMA_VERSION = "canonical-catalog-v1"
_CN = ZoneInfo("Asia/Shanghai")


def canonical_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def canonical_schema_definition() -> list[dict]:
    """Formal canonical schema definition (column name -> pyarrow type + note)."""
    return [
        {"name": "provider", "type": "string"},
        {"name": "source_type", "type": "string"},
        {"name": "exchange", "type": "string"},
        {"name": "concrete_contract", "type": "string"},
        {"name": "product", "type": "string"},
        {"name": "trading_day", "type": "date32"},
        {"name": "bar_start", "type": "timestamp[us] tz=Asia/Shanghai"},
        {"name": "bar_end", "type": "timestamp[us] tz=Asia/Shanghai"},
        {"name": "historical_available_at", "type": "timestamp[us] tz=Asia/Shanghai"},
        {"name": "open", "type": "decimal128(24,4)"},
        {"name": "high", "type": "decimal128(24,4)"},
        {"name": "low", "type": "decimal128(24,4)"},
        {"name": "close", "type": "decimal128(24,4)"},
        {"name": "volume", "type": "int64"},
        {"name": "open_interest_start", "type": "int64 nullable"},
        {"name": "open_interest_end", "type": "int64 nullable"},
        {"name": "raw_artifact_identity_id", "type": "string"},
        {"name": "source_identity_id", "type": "string"},
        {"name": "data_version_id", "type": "string"},
        {"name": "contract_metadata_identity", "type": "string"},
        {"name": "session_metadata_identity", "type": "string"},
        {"name": "normalizer_identity", "type": "string"},
        {"name": "schema_version", "type": "string"},
        {"name": "year", "type": "int32 (partition)"},
        {"name": "month", "type": "int32 (partition)"},
    ]


def _pyarrow():
    try:
        import pyarrow as pa  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise RuntimeError(
            "pyarrow is required for canonical Parquet storage; it is a pinned "
            "canonical-build dependency (tested version 25.0.1)"
        ) from exc
    return pa


def canonical_parquet_schema():
    """The canonical pyarrow schema (partition columns included)."""
    pa = _pyarrow()
    return pa.schema(
        [
            ("provider", pa.string()),
            ("source_type", pa.string()),
            ("exchange", pa.string()),
            ("concrete_contract", pa.string()),
            ("product", pa.string()),
            ("trading_day", pa.date32()),
            ("bar_start", pa.timestamp("us", tz="Asia/Shanghai")),
            ("bar_end", pa.timestamp("us", tz="Asia/Shanghai")),
            ("historical_available_at", pa.timestamp("us", tz="Asia/Shanghai")),
            ("open", pa.decimal128(24, 4)),
            ("high", pa.decimal128(24, 4)),
            ("low", pa.decimal128(24, 4)),
            ("close", pa.decimal128(24, 4)),
            ("volume", pa.int64()),
            ("open_interest_start", pa.int64()),
            ("open_interest_end", pa.int64()),
            ("raw_artifact_identity_id", pa.string()),
            ("source_identity_id", pa.string()),
            ("data_version_id", pa.string()),
            ("contract_metadata_identity", pa.string()),
            ("session_metadata_identity", pa.string()),
            ("normalizer_identity", pa.string()),
            ("schema_version", pa.string()),
            ("year", pa.int32()),
            ("month", pa.int32()),
        ]
    )


PARTITION_COLUMNS = ("exchange", "product", "concrete_contract", "year", "month")


@dataclass(frozen=True)
class CanonicalRow:
    """One normalized bar in canonical storage form.

    OHLC are exact Decimals (never silently rounded); string forms are used
    only for stable identity hashing.
    """

    provider: str
    source_type: str
    exchange: str
    concrete_contract: str
    product: str
    trading_day: date
    bar_start: datetime
    bar_end: datetime
    historical_available_at: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    open_interest_start: int | None
    open_interest_end: int | None
    raw_artifact_identity_id: str
    source_identity_id: str
    data_version_id: str
    contract_metadata_identity: str
    session_metadata_identity: str
    normalizer_identity: str

    def __post_init__(self) -> None:
        prices = (self.open, self.high, self.low, self.close)
        if any(type(v) is not Decimal or not v.is_finite() or v <= 0 for v in prices):
            raise ValueError("canonical row OHLC must be positive finite Decimals")
        if self.low > min(self.open, self.close) or self.high < max(self.open, self.close) or self.low > self.high:
            raise ValueError("canonical row OHLC is inconsistent")
        if type(self.volume) is not int or self.volume < 0:
            raise ValueError("canonical row volume must be a non-negative integer")

    def to_pylist_row(self) -> dict:
        return {
            "provider": self.provider,
            "source_type": self.source_type,
            "exchange": self.exchange,
            "concrete_contract": self.concrete_contract,
            "product": self.product,
            "trading_day": self.trading_day,
            "bar_start": self.bar_start,
            "bar_end": self.bar_end,
            "historical_available_at": self.historical_available_at,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "open_interest_start": self.open_interest_start,
            "open_interest_end": self.open_interest_end,
            "raw_artifact_identity_id": self.raw_artifact_identity_id,
            "source_identity_id": self.source_identity_id,
            "data_version_id": self.data_version_id,
            "contract_metadata_identity": self.contract_metadata_identity,
            "session_metadata_identity": self.session_metadata_identity,
            "normalizer_identity": self.normalizer_identity,
            "schema_version": CANONICAL_SCHEMA_VERSION,
            "year": self.trading_day.year,
            "month": self.trading_day.month,
        }

    def to_stable_dict(self) -> dict:
        """Stable string form for deterministic identity hashing."""
        return {
            "provider": self.provider,
            "source_type": self.source_type,
            "exchange": self.exchange,
            "concrete_contract": self.concrete_contract,
            "product": self.product,
            "trading_day": self.trading_day.isoformat(),
            "bar_start": self.bar_start.isoformat(),
            "bar_end": self.bar_end.isoformat(),
            "historical_available_at": self.historical_available_at.isoformat(),
            "open": str(self.open),
            "high": str(self.high),
            "low": str(self.low),
            "close": str(self.close),
            "volume": self.volume,
            "open_interest_start": self.open_interest_start,
            "open_interest_end": self.open_interest_end,
            "raw_artifact_identity_id": self.raw_artifact_identity_id,
            "source_identity_id": self.source_identity_id,
            "data_version_id": self.data_version_id,
            "contract_metadata_identity": self.contract_metadata_identity,
            "session_metadata_identity": self.session_metadata_identity,
            "normalizer_identity": self.normalizer_identity,
            "schema_version": CANONICAL_SCHEMA_VERSION,
            "year": self.trading_day.year,
            "month": self.trading_day.month,
        }


def write_partition_table(root: Path, rows: Iterable[CanonicalRow]) -> dict:
    """Write a logical canonical table under the partitioned layout.

    Returns deterministic storage facts: partition-relative file paths, per-file
    SHA256, row count, and a logical table identity (hash of sorted rows).
    """
    pa = _pyarrow()
    import pyarrow.parquet as pq  # noqa: PLC0415

    row_objects = list(rows)
    if not row_objects:
        raise ValueError("cannot write an empty canonical partition")
    row_list = [row.to_pylist_row() for row in row_objects]
    table = pa.Table.from_pylist(row_list, schema=canonical_parquet_schema())
    table = table.select([f.name for f in canonical_parquet_schema()])
    # partition columns must be non-null for partitioning
    root_path = Path(root)
    root_path.mkdir(parents=True, exist_ok=True)
    pq.write_to_dataset(
        table,
        root_path=str(root_path),
        partition_cols=list(PARTITION_COLUMNS),
        schema=canonical_parquet_schema(),
        existing_data_behavior="overwrite_or_ignore",
    )
    files = sorted(p for p in root_path.rglob("*.parquet") if p.is_file())
    if not files:
        raise RuntimeError("no parquet files written")
    inventory = [
        {
            "relative_path": str(p.relative_to(root_path)).replace("\\", "/"),
            "sha256": sha256(p.read_bytes()).hexdigest(),
            "bytes": p.stat().st_size,
        }
        for p in files
    ]
    # logical table identity: stable hash of the canonical rows
    logical = canonical_hash(
        [row.to_stable_dict() for row in sorted(row_objects, key=lambda r: r.bar_start.isoformat())]
    )
    return {
        "row_count": len(row_list),
        "file_count": len(files),
        "files": inventory,
        "logical_table_identity": logical,
        "storage_version": PARQUET_STORAGE_VERSION,
        "schema_version": CANONICAL_SCHEMA_VERSION,
    }


def read_partition_table(root: Path):
    """Read the partitioned dataset and cast back to the canonical schema.

    Partition columns are restored dictionary-encoded by pyarrow; select+cast
    restores the stable canonical types so write/read logical equality holds.
    """
    pa = _pyarrow()
    import pyarrow.parquet as pq  # noqa: PLC0415

    table = pq.read_table(root)
    schema = canonical_parquet_schema()
    table = table.select([f.name for f in schema]).cast(schema).combine_chunks()
    return table


def verify_round_trip(root: Path, expected_rows: list[dict]) -> bool:
    """Verify Parquet write/read logical equality against expected rows."""
    pa = _pyarrow()
    schema = canonical_parquet_schema()
    expected = pa.Table.from_pylist(expected_rows, schema=schema).select([f.name for f in schema]).combine_chunks()
    actual = read_partition_table(root)
    return expected.equals(actual)


@dataclass(frozen=True)
class CatalogPartitionEntry:
    provider: str
    contract: str
    exchange: str
    granularity_seconds: int
    trading_day: date
    raw_sha256: str
    request_identity: str
    data_version_id: str
    normalized_batch_id: str
    parquet_artifact_identity: str
    parquet_logical_identity: str
    parquet_storage_version: str
    row_count: int
    coverage_start: str
    coverage_end: str
    quality_status: str


_CATALOG_DDL = """
CREATE TABLE IF NOT EXISTS catalog_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS partition_entries (
    partition_key TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    contract TEXT NOT NULL,
    exchange TEXT NOT NULL,
    granularity_seconds INTEGER NOT NULL,
    trading_day TEXT NOT NULL,
    raw_sha256 TEXT NOT NULL,
    request_identity TEXT NOT NULL,
    data_version_id TEXT NOT NULL,
    normalized_batch_id TEXT NOT NULL,
    parquet_artifact_identity TEXT NOT NULL,
    parquet_logical_identity TEXT NOT NULL,
    parquet_storage_version TEXT NOT NULL,
    row_count INTEGER NOT NULL,
    coverage_start TEXT NOT NULL,
    coverage_end TEXT NOT NULL,
    quality_status TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_partition_entries_contract ON partition_entries(contract);
CREATE INDEX IF NOT EXISTS idx_partition_entries_trading_day ON partition_entries(trading_day);
"""


class CanonicalCatalog:
    """Rebuildable SQLite catalog/index over accepted canonical partitions.

    This is a local deterministic index only; it is not the historical truth
    authority (committed immutable manifests/evidence are).  It can be rebuilt
    from accepted manifests + parquet inventory via ``rebuild_from_manifest``.
    """

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path))
        self._conn.executescript(_CATALOG_DDL)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def set_meta(self, key: str, value: str) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO catalog_meta(key, value) VALUES (?, ?)", (key, value)
        )
        self._conn.commit()

    def get_meta(self, key: str) -> str | None:
        row = self._conn.execute("SELECT value FROM catalog_meta WHERE key = ?", (key,)).fetchone()
        return None if row is None else row[0]

    def upsert_partition(self, entry: CatalogPartitionEntry) -> None:
        self._conn.execute(
            """
            INSERT OR REPLACE INTO partition_entries (
                partition_key, provider, contract, exchange, granularity_seconds,
                trading_day, raw_sha256, request_identity, data_version_id,
                normalized_batch_id, parquet_artifact_identity,
                parquet_logical_identity, parquet_storage_version, row_count,
                coverage_start, coverage_end, quality_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"{entry.provider}|{entry.contract}|{entry.granularity_seconds}|{entry.trading_day.isoformat()}",
                entry.provider,
                entry.contract,
                entry.exchange,
                entry.granularity_seconds,
                entry.trading_day.isoformat(),
                entry.raw_sha256,
                entry.request_identity,
                entry.data_version_id,
                entry.normalized_batch_id,
                entry.parquet_artifact_identity,
                entry.parquet_logical_identity,
                entry.parquet_storage_version,
                entry.row_count,
                entry.coverage_start,
                entry.coverage_end,
                entry.quality_status,
            ),
        )
        self._conn.commit()

    def partition_count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM partition_entries").fetchone()[0]

    def row_count_total(self) -> int:
        return self._conn.execute("SELECT COALESCE(SUM(row_count), 0) FROM partition_entries").fetchone()[0]

    def query(self, *, product: str | None = None, year: int | None = None) -> list[dict]:
        sql = "SELECT * FROM partition_entries"
        clauses: list[str] = []
        params: list = []
        if product is not None:
            clauses.append("contract LIKE ?")
            params.append(f"SHFE.{product}%")
        if year is not None:
            clauses.append("trading_day LIKE ?")
            params.append(f"{year}-%")
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY partition_key"
        cols = [d[0] for d in self._conn.execute("SELECT * FROM partition_entries").description]
        return [dict(zip(cols, row)) for row in self._conn.execute(sql, params)]

    def identity(self) -> str:
        rows = self._conn.execute("SELECT partition_key, raw_sha256, data_version_id, row_count FROM partition_entries ORDER BY partition_key").fetchall()
        meta = dict(self._conn.execute("SELECT key, value FROM catalog_meta ORDER BY key").fetchall())
        return canonical_hash(
            {
                "schema_version": SQLITE_CATALOG_SCHEMA_VERSION,
                "meta": meta,
                "partitions": rows,
            }
        )


def rebuild_catalog_from_manifest(catalog: CanonicalCatalog, entries: Iterable[CatalogPartitionEntry]) -> None:
    """Deterministically (re)build the catalog from accepted partition facts."""
    for entry in sorted(entries, key=lambda e: (e.contract, e.trading_day.isoformat())):
        catalog.upsert_partition(entry)
    catalog.set_meta("schema_version", SQLITE_CATALOG_SCHEMA_VERSION)
    catalog.set_meta("rebuildable", "yes-from-accepted-manifest")

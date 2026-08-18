"""Merge per-product canonical catalogs into the single catalog.sqlite.

The parallel normalize writes one SQLite catalog per product to avoid
cross-process writer contention ("database is locked" under shared WAL).  This
tool combines them back into the canonical single catalog (rebuildable index).

Usage (pyarrow venv):
  python -m tools.merge_catalogs
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from src.canonical_storage import _CATALOG_DDL

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CATALOG = PROJECT_ROOT / "data" / "canonical" / "catalog.sqlite"
CATALOG_DIR = PROJECT_ROOT / "data" / "canonical"
PRODUCTS = ("cu", "al", "ni", "au", "ag", "rb")


def _count(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM partition_entries").fetchone()[0]


def main() -> None:
    conn = sqlite3.connect(str(CATALOG))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=60000")
    conn.executescript(_CATALOG_DDL)
    merged = 0
    for product in PRODUCTS:
        prod_path = CATALOG_DIR / f"catalog-{product}.sqlite"
        if not prod_path.exists():
            raise SystemExit(f"missing product catalog: {prod_path}")
        conn.execute(f"ATTACH DATABASE ? AS prod", (str(prod_path),))
        try:
            before = _count(conn)
            conn.execute(
                "INSERT OR REPLACE INTO partition_entries SELECT * FROM prod.partition_entries"
            )
            conn.execute(
                "INSERT OR REPLACE INTO catalog_meta SELECT * FROM prod.catalog_meta"
            )
            # Commit before DETACH: an open read transaction holds a lock on the
            # attached database and DETACH then fails with 'database is locked'.
            conn.commit()
            added = _count(conn) - before
            merged += added
            print(f"{product}: merged {added} (running {_count(conn)})")
        finally:
            conn.execute("DETACH DATABASE prod")
    conn.commit()
    total = _count(conn)
    rows = conn.execute("SELECT COALESCE(SUM(row_count),0) FROM partition_entries").fetchone()[0]
    print(f"MERGE total={total} rows={rows} merged_new={merged}")
    conn.close()


if __name__ == "__main__":
    main()

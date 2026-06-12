"""
Sync production SQLite data to local dev.

Usage:
    python3 scripts/sync_from_prod.py                  # download full DB
    python3 scripts/sync_from_prod.py [table1 table2]  # sync specific tables only (legacy mode)

ASTRAL_PROD_URL is read from .env if not already set in the environment.
No auth token needed — IP allowlist only.
"""

import os
import sqlite3
import sys
import urllib.request
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.utils.config import ASTRAL_CONFIG  # noqa: E402

# Load ASTRAL_PROD_URL from .env if not in environment
if not os.environ.get("ASTRAL_PROD_URL"):
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("ASTRAL_PROD_URL="):
                os.environ["ASTRAL_PROD_URL"] = line.split("=", 1)[1].strip()
                break

PROD_URL = os.environ.get("ASTRAL_PROD_URL", "").rstrip("/")
LOCAL_DB = ASTRAL_CONFIG["db_dir"] / "astral.db"


def _get(path: str) -> dict:
    url = f"{PROD_URL}/api/admin/data{path}"
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.loads(resp.read())


def _local_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]


def _local_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [r[0] for r in rows]


def sync_table(conn: sqlite3.Connection, table: str) -> str:
    # Schema check — fetch prod columns only first
    prod_schema = _get(f"/table/{table}?schema_only=1")
    prod_cols = prod_schema["columns"]
    local_cols = _local_columns(conn, table)

    if prod_cols != local_cols:
        return f"SKIP  {table} — schema mismatch\n      prod:  {prod_cols}\n      local: {local_cols}"

    # Fetch all rows from prod
    prod_data = _get(f"/table/{table}")
    rows = prod_data["rows"]
    placeholders = ", ".join("?" * len(prod_cols))
    col_list = ", ".join(prod_cols)

    conn.execute(f"DELETE FROM {table}")
    if rows:
        conn.executemany(f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})", rows)

    return f"OK    {table} — {len(rows)} rows"


def download_db():
    """Download the full prod SQLite file and overwrite local DB."""
    url = f"{PROD_URL}/api/admin/data/download"
    print(f"Downloading {url} → {LOCAL_DB} ...")
    LOCAL_DB.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as resp:
        LOCAL_DB.write_bytes(resp.read())
    size_mb = LOCAL_DB.stat().st_size / 1_048_576
    print(f"Done — {size_mb:.1f} MB written.")


def main():
    if not PROD_URL:
        print("ERROR: ASTRAL_PROD_URL is not set (checked env and .env).")
        sys.exit(1)

    requested = sys.argv[1:]
    if not requested:
        # Default: full DB download
        download_db()
        return

    # Legacy: sync specific tables only
    conn = sqlite3.connect(str(LOCAL_DB))
    conn.row_factory = sqlite3.Row
    results = []
    try:
        for table in requested:
            local_all = _local_tables(conn)
            if table not in local_all:
                results.append(f"SKIP  {table} — not in local DB")
                continue
            try:
                results.append(sync_table(conn, table))
                conn.commit()
            except Exception as e:
                conn.rollback()
                results.append(f"ERROR {table} — {e}")
    finally:
        conn.close()
    print("\n".join(results))


if __name__ == "__main__":
    main()

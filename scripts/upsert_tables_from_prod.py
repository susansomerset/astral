#!/usr/bin/env python3
"""
Upsert selected config tables from production into the local SQLite DB (merge, not wipe).

Fetches rows via the same HTTP API as scripts/sync_from_prod.py (ASTRAL_PROD_URL,
IP allowlist on prod). Tables and merge rules live in src.data.database.

Usage:
    python3 scripts/upsert_tables_from_prod.py              # all three tables
    python3 scripts/upsert_tables_from_prod.py agent_task candidate
    python3 scripts/upsert_tables_from_prod.py --dry-run  # fetch + counts only

ASTRAL_PROD_URL is read from the environment or from .env in the repo root (same as sync_from_prod).
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.utils.config import ASTRAL_CONFIG  # noqa: E402
from src.data.database import (  # noqa: E402
    ALLOWED_CONFIG_TABLES,
    apply_config_table_upsert,
    table_columns,
)

if not os.environ.get("ASTRAL_PROD_URL"):
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("ASTRAL_PROD_URL="):
                os.environ["ASTRAL_PROD_URL"] = line.split("=", 1)[1].strip()
                break

PROD_URL = (os.environ.get("ASTRAL_PROD_URL") or "").rstrip("/")
LOCAL_DB = ASTRAL_CONFIG["db_dir"] / "astral.db"


def _prod_get(path: str, timeout: int = 120) -> dict:
    url = f"{PROD_URL}/api/admin/data{path}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:800]
        raise RuntimeError(f"HTTP {e.code} from prod {url}: {body or e.reason}") from e


def upsert_table(conn: sqlite3.Connection, table: str, dry_run: bool) -> str:
    prod_schema = _prod_get(f"/table/{table}?schema_only=1", timeout=60)
    prod_cols = prod_schema["columns"]
    local_cols = table_columns(conn, table)
    if prod_cols != local_cols:
        raise RuntimeError(
            f"{table}: column list mismatch (prod vs local). Align schemas first.\n"
            f"  prod:  {prod_cols}\n  local: {local_cols}"
        )

    prod_data = _prod_get(f"/table/{table}", timeout=180)
    rows: list[list] = prod_data["rows"]
    if dry_run:
        return f"DRY   {table} — would upsert {len(rows)} prod row(s)"

    r = apply_config_table_upsert(conn, table, prod_cols, rows)
    if table == "dispatch_task":
        return f"OK    {table} — {len(rows)} prod row(s): {r['updated']} updated, {r['inserted']} inserted"
    return f"OK    {table} — INSERT OR REPLACE {r['replaced']} row(s)"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "tables",
        nargs="*",
        help=f"Subset of: {', '.join(sorted(ALLOWED_CONFIG_TABLES))} (default: all)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Fetch prod data and print counts only")
    args = parser.parse_args()

    if not PROD_URL:
        print("ERROR: ASTRAL_PROD_URL is not set (checked env and .env).", file=sys.stderr)
        sys.exit(1)

    names = [t.strip() for t in args.tables if t.strip()]
    if not names:
        names = sorted(ALLOWED_CONFIG_TABLES)
    bad = [t for t in names if t not in ALLOWED_CONFIG_TABLES]
    if bad:
        print(f"ERROR: unsupported table(s): {bad}. Allowed: {sorted(ALLOWED_CONFIG_TABLES)}", file=sys.stderr)
        sys.exit(1)

    if not LOCAL_DB.exists():
        print(f"ERROR: local database not found: {LOCAL_DB}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(str(LOCAL_DB))
    conn.row_factory = sqlite3.Row
    lines: list[str] = []
    try:
        for table in names:
            try:
                lines.append(upsert_table(conn, table, args.dry_run))
                if not args.dry_run:
                    conn.commit()
            except Exception as e:
                if not args.dry_run:
                    conn.rollback()
                lines.append(f"ERROR {table} — {e}")
    finally:
        conn.close()
    print("\n".join(lines))


if __name__ == "__main__":
    main()

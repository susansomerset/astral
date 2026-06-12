#!/usr/bin/env python3
"""
Push selected config tables from the local SQLite DB to production (merge, not full replace).

Reads local rows, then POSTs them to the deployed app, which applies the same upsert rules as
src.data.database (dispatch_task by natural key preserving prod id on update;
agent_task / candidate INSERT OR REPLACE).

Requires:
  - ASTRAL_PROD_URL — base URL of production (from env or repo .env)
  - Your outbound IP on production's ASTRAL_ALLOWED_IPS (same as sync_from_prod)
  - Authorization: Bearer token (default matches src/ui/frontend stub; override with ASTRAL_ADMIN_BEARER)

Deploy the version of Astral that includes POST /api/admin/data/upsert_config_table before using this.

Usage:
    python3 scripts/push_tables_to_prod.py
    python3 scripts/push_tables_to_prod.py dispatch_task agent_task
    python3 scripts/push_tables_to_prod.py --dry-run
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
from src.data.database import ALLOWED_CONFIG_TABLES, table_columns  # noqa: E402

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
# Same default as src/ui/frontend/src/lib/api.ts until Auth0
BEARER = (os.environ.get("ASTRAL_ADMIN_BEARER") or "stub-susan-token").strip()


def _post_json(path: str, payload: dict, timeout: int = 180) -> dict:
    url = f"{PROD_URL}/api/admin{path}"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {BEARER}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")[:1200]
        try:
            err_obj = json.loads(raw)
            detail = err_obj.get("error", raw)
        except json.JSONDecodeError:
            detail = raw or str(e.reason)
        raise RuntimeError(f"HTTP {e.code} {url}: {detail}") from e


def push_table(conn: sqlite3.Connection, table: str, dry_run: bool) -> str:
    cols = table_columns(conn, table)
    rows = [list(r) for r in conn.execute(f"SELECT * FROM {table}").fetchall()]
    if dry_run:
        return f"DRY   {table} — would push {len(rows)} local row(s) to prod"

    result = _post_json(
        "/data/upsert_config_table",
        {"table": table, "columns": cols, "rows": rows},
    )
    if not result.get("ok"):
        raise RuntimeError(result.get("error", str(result)))
    if table == "dispatch_task":
        return (
            f"OK    {table} — pushed {result.get('rows')} row(s): "
            f"{result.get('updated', 0)} updated, {result.get('inserted', 0)} inserted on prod"
        )
    return f"OK    {table} — INSERT OR REPLACE {result.get('replaced', 0)} row(s) on prod"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "tables",
        nargs="*",
        help=f"Subset of: {', '.join(sorted(ALLOWED_CONFIG_TABLES))} (default: all)",
    )
    parser.add_argument("--dry-run", action="store_true")
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
                lines.append(push_table(conn, table, args.dry_run))
            except Exception as e:
                lines.append(f"ERROR {table} — {e}")
    finally:
        conn.close()
    print("\n".join(lines))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Backfill NULL last_run_at in dispatch_task to current UTC timestamp."""

import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.config import ASTRAL_CONFIG

db_path = ASTRAL_CONFIG["db_dir"] / "astral.db"
now = datetime.now(timezone.utc).isoformat()

conn = sqlite3.connect(str(db_path))
cur = conn.execute("UPDATE dispatch_task SET last_run_at = ? WHERE last_run_at IS NULL", (now,))
conn.commit()
print(f"Updated {cur.rowcount} row(s) — last_run_at set to {now}")
conn.close()

#!/usr/bin/env python3
"""Decrypt candidate.api_keys ciphertext, upsert one Railway variable per key, then clear ciphertext.

Copy the database first. --execute calls Railway. Default is dry-run and prints no plaintext.

  cp data/astral.db data/astral.db.pre-AST-2251
  python scripts/migrations/migrate_candidate_api_keys_to_railway.py
  python scripts/migrations/migrate_candidate_api_keys_to_railway.py --execute
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.data.database import (
    candidate_secret_rows_from_column,
    decrypt_value,
    list_candidate_api_key_columns,
    replace_candidate_secret_rows,
)
from src.external.railway import upsert_service_variable
from src.utils.config import candidate_secret_variable_name
from src.utils.logging import get_logger

logger = get_logger(__name__)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--execute", action="store_true", help="Upsert and clear ciphertext (default is dry-run)")
    args = ap.parse_args()
    for col in list_candidate_api_key_columns():
        cid = col["astral_candidate_id"]
        stored = candidate_secret_rows_from_column(col["api_keys"])
        ciphertext = [row for row in stored if "key" in row and "status" not in row]
        if not ciphertext:
            continue
        remembered: dict = {}
        for entry in ciphertext:
            server = entry["server"]
            name = candidate_secret_variable_name(server, cid)
            if not args.execute:
                try:
                    decrypt_value(entry["key"])
                except (RuntimeError, ValueError):
                    print(f"undecryptable {cid} {server}")
                else:
                    print(f"would upsert {cid} {server} {name}")
                continue
            try:
                plaintext = decrypt_value(entry["key"])
            except (RuntimeError, ValueError):
                logger.warning(
                    "%s secret %s ciphertext would not decrypt — status NOT SET",
                    cid,
                    server,
                )
                remembered[server] = {"server": server, "status": "NOT SET", "expires_at": None}
                continue
            # RailwayCallFailed is already logged in the client. Abort before this row is rewritten.
            upsert_service_variable(name=name, value=plaintext)
            remembered[server] = {"server": server, "status": "SET", "expires_at": None}
        if not args.execute:
            continue
        replacement = []
        for row in stored:
            if "key" in row and "status" not in row and row["server"] in remembered:
                replacement.append(remembered[row["server"]])
            else:
                replacement.append(row)
        replace_candidate_secret_rows(cid, replacement)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

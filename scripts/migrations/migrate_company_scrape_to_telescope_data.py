#!/usr/bin/env python3
"""
Move existing company scrape text out of company_data into telescope_data (AST-2135).

Three modes, run separately:
  export — read every company's scraped keys; write a JSON file of telescope rows (pre-assigned
           uuids) and, per company, the id-shaped value each key should hold. No DB writes.
  load   — insert the file's rows into telescope_data by uuid; a re-run adds nothing.
  clear  — swap each exported key in company_data to its row id(s). Keys changed since export
           are left as they are.

Run export → load → clear in that order; clear refuses while any referenced row is missing.

--db-dir pins ASTRAL_DB_DIR (the folder holding astral.db) for this run; without it the
app's ASTRAL_DB_DIR is used. The DB path is printed first, before anything else happens.

Usage:
  python scripts/migrations/migrate_company_scrape_to_telescope_data.py export --file scrape.json
  python scripts/migrations/migrate_company_scrape_to_telescope_data.py load --file scrape.json
  python scripts/migrations/migrate_company_scrape_to_telescope_data.py clear --file scrape.json
  python scripts/migrations/migrate_company_scrape_to_telescope_data.py export --file /tmp/x.json --db-dir /tmp/copy
"""

import argparse
import hashlib
import json
import os
import sys
import uuid
from collections import Counter
from pathlib import Path
from typing import Any


def _digest(value: Any) -> str:
    """Stable fingerprint of a company_data value — clear only swaps a key still holding what export saw."""
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode("utf-8")).hexdigest()


def _export(file_path: Path) -> int:
    from src.core.gazer import is_telescope_id
    from src.core.roster import _assemble_pjl_content, _rebuilt_pjl_nav_links
    from src.data.database import DB_PATH, _utc_now, list_companies
    from src.utils.config import TELESCOPE_DATA_CONFIG
    from src.utils.logging import get_logger

    log = get_logger(__name__)
    if file_path.exists():
        # Never replace a file a load may already have used — its uuids are the stored ids.
        print(f"Refusing: {file_path} already exists")
        return 2
    vt = TELESCOPE_DATA_CONFIG["data_types"]["VISIBLE_TEXT"]
    pl = TELESCOPE_DATA_CONFIG["data_types"]["PAGE_LINKS"]
    created_at = _utc_now()
    rows: dict[str, dict[str, Any]] = {}
    companies: dict[str, dict[str, Any]] = {}
    warnings = 0

    def _text(v: Any) -> bool:
        # Legacy page text: a non-blank string that isn't already a row id.
        return isinstance(v, str) and bool(v.strip()) and not is_telescope_id(v)

    log.debug("Calling list_companies: []")
    all_companies = list_companies()
    log.debug("Response from list_companies: %s", all_companies)
    for company in all_companies:
        sn = company["short_name"]
        cd = company.get("company_data") or {}
        cid = company.get("candidate_id")
        # Same URLs roster's writers record: homepage/nav on the website, job_list_visible on the job page.
        site = (company.get("company_website") or company.get("job_site") or "").strip()
        job_url = (company.get("job_site") or site).strip()
        rows_before = len(rows)

        def _new_row(url: str, data_type: str, content: str, cid: Any = cid) -> str:
            # Content verbatim — legacy values are already in the shape readers return.
            rid = str(uuid.uuid4())
            rows[rid] = {"candidate_id": cid, "url": url, "data_type": data_type,
                         "content": content, "created_at": created_at}
            return rid

        keys: dict[str, dict[str, Any]] = {}
        for key in TELESCOPE_DATA_CONFIG["company_data_id_keys"]:
            v = cd.get(key)
            if v is None:
                continue
            new: Any = v
            skipped = 0
            if key in ("homepage_text", "job_list_visible") and _text(v):
                new = _new_row(site if key == "homepage_text" else job_url, vt, v)
            elif key == "nav_links" and _text(v):
                new = _new_row(site, pl, v)
            elif key == "website_content" and _text(v):
                new = _new_row(site, vt, v)  # oldest shape: one plain string
            elif key == "website_content" and isinstance(v, list):
                new = []
                for e in v:
                    # {url, content} in that order is exactly what the resolver rebuilds from {url, id}.
                    if isinstance(e, dict) and list(e) == ["url", "content"] and _text(e["content"]):
                        new.append({"url": e["url"], "id": _new_row(e["url"], vt, e["content"])})
                    else:
                        # Ids and blank pages are fine as they are; text we couldn't move is not.
                        skipped += not isinstance(e, dict) or _text(e.get("content"))
                        new.append(e)
            elif key == "pjl_scrape_pages" and isinstance(v, list):
                new = []
                for e in v:
                    # Legacy merge rows only ever held these three keys; anything else the resolver would drop.
                    if (isinstance(e, dict) and set(e) <= {"url", "visible_text", "enumerated_nav_links"}
                            and _text(e.get("visible_text"))):
                        page = {"url": e.get("url") or "", "id": _new_row(e.get("url") or "", vt, e["visible_text"])}
                        if _text(e.get("enumerated_nav_links")):
                            page["links_id"] = _new_row(page["url"], pl, e["enumerated_nav_links"])
                        new.append(page)
                    else:
                        skipped += not isinstance(e, dict) or _text(e.get("visible_text"))
                        new.append(e)
            elif not (isinstance(v, str) and (not v.strip() or is_telescope_id(v))):
                skipped = 1  # a shape no reader writes — leave it alone
            if skipped:
                warnings += 1
                log.warning("%s %s: %d value(s) not migrated (unexpected shape) — left as text", sn, key, skipped)
            if new != v:
                keys[key] = {"was": _digest(v), "value": new}
            else:
                log.debug("%s %s: nothing to move", sn, key)

        if "pjl_scrape_pages" in keys:
            # Derived fields go NULL only when rebuild-on-read gives today's text (AC 6 over AC 5).
            pages = cd["pjl_scrape_pages"]
            stored_asm = cd.get("pjl_assembled_content")
            if stored_asm is not None:
                log.debug("Calling _assemble_pjl_content: %s", pages)
                rebuilt_asm = _assemble_pjl_content(pages)
                log.debug("Response from _assemble_pjl_content: %s", rebuilt_asm)
                # Its only reader strips it and assembles the pages when it is empty.
                if not str(stored_asm).strip() or str(stored_asm).strip() == rebuilt_asm:
                    keys["pjl_assembled_content"] = {"was": _digest(stored_asm), "value": None}
                else:
                    warnings += 1
                    log.warning("%s pjl_assembled_content: stored text differs from rebuild — left stored", sn)
            stored_nav = cd.get("pjl_nav_links")
            if stored_nav is not None:
                log.debug("Calling _rebuilt_pjl_nav_links: %s", cd)
                rebuilt_nav = _rebuilt_pjl_nav_links(cd)
                log.debug("Response from _rebuilt_pjl_nav_links: %s", rebuilt_nav)
                # Exact match — one reader uses it unstripped.
                if stored_nav == rebuilt_nav:
                    keys["pjl_nav_links"] = {"was": _digest(stored_nav), "value": None}
                else:
                    warnings += 1
                    log.warning("%s pjl_nav_links: stored text differs from rebuild — left stored", sn)

        if keys:
            companies[sn] = {"keys": keys}
            log.info("%s | company scrape exported: %d rows, keys %s (batch: -)",
                     sn, len(rows) - rows_before, ",".join(keys))

    file_path.write_text(json.dumps(
        {"exported_at": created_at, "db_path": str(DB_PATH), "rows": rows, "companies": companies}, indent=2,
    ))
    by_type = Counter(r["data_type"] for r in rows.values())
    print(f"Companies scanned: {len(all_companies)}  with changes: {len(companies)}")
    print(f"Rows: {len(rows)}  " + "  ".join(f"{t}={n}" for t, n in sorted(by_type.items())))
    print(f"Warnings: {warnings}")
    print(f"Wrote {file_path}")
    return 0


def _load(file_path: Path) -> int:
    from src.data.database import (
        _compress_payload,
        _ensure_telescope_data_schema,
        _get_connection,
    )
    from src.utils.logging import get_logger

    log = get_logger(__name__)
    rows = json.loads(file_path.read_text())["rows"]
    # Raw INSERT, not save_telescope_data: that mints its own uuid, and the file's ids must be the
    # stored ids — that is what makes a re-run add nothing.
    conn = _get_connection()
    try:
        _ensure_telescope_data_schema(conn)
        log.debug("Calling INSERT OR IGNORE telescope_data: %s", list(rows))
        inserted = 0
        for rid, r in rows.items():
            cur = conn.execute(
                "INSERT OR IGNORE INTO telescope_data"
                " (telescope_data_id, candidate_id, url, data_type, content, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (rid, r["candidate_id"], r["url"], r["data_type"], _compress_payload(r["content"]), r["created_at"]),
            )
            inserted += cur.rowcount
        conn.commit()
        log.debug("Response from INSERT OR IGNORE telescope_data: inserted=%d", inserted)
    finally:
        conn.close()
    print(f"Rows in file: {len(rows)}  inserted: {inserted}  already present: {len(rows) - inserted}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Move company scrape text into telescope_data (AST-2135).")
    parser.add_argument("mode", choices=("export", "load", "clear"))
    parser.add_argument("--file", required=True, help="Export JSON path (written by export, read by load/clear).")
    parser.add_argument("--db-dir", help="Folder holding astral.db; defaults to the app's ASTRAL_DB_DIR.")
    args = parser.parse_args()
    if args.db_dir:
        # Must be set before any src import: config reads ASTRAL_DB_DIR at import time and the
        # logger writes app_log into that same DB.
        os.environ["ASTRAL_DB_DIR"] = str(Path(args.db_dir).resolve())
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.data.database import DB_PATH

    print(f"DB: {DB_PATH}")
    file_path = Path(args.file)
    return {"export": _export, "load": _load}[args.mode](file_path)


if __name__ == "__main__":
    sys.exit(main())

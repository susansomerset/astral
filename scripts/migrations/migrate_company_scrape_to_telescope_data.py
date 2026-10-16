#!/usr/bin/env python3
"""
Move existing company scrape text out of company_data into web_data (AST-2135).

Three modes, run separately:
  export — read every company's scraped keys; write a JSON file of telescope rows (pre-assigned
           uuids) and, per company, the id-shaped value each key should hold. No DB writes.
           pjl_nav_links is not migrated: any stored value is set to NULL (readers rebuild it).
  load   — insert the file's rows into web_data by uuid; a re-run adds nothing.
  clear  — swap each exported key in company_data to its row id(s). Keys changed since export
           are left as they are.

  dump   — after clear: write chunked JSON files (arrays of column-keyed rows) of the new web_data
           rows and the changed company rows, for pasting into the admin Copy Output upsert. No DB writes.

Run export → load → clear in that order; clear refuses while any referenced row is missing.
dump refuses until clear has run.

--db-dir pins ASTRAL_DB_DIR (the folder holding astral.db) for this run; without it the
app's ASTRAL_DB_DIR is used. The DB path is printed first, before anything else happens.

Usage:
  python scripts/migrations/migrate_company_scrape_to_telescope_data.py export --file scrape.json
  python scripts/migrations/migrate_company_scrape_to_telescope_data.py load --file scrape.json
  python scripts/migrations/migrate_company_scrape_to_telescope_data.py clear --file scrape.json
  python scripts/migrations/migrate_company_scrape_to_telescope_data.py dump --file scrape.json --out-dir upsert_files --chunk-mb 4
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
    from src.core.roster import _assemble_pjl_content
    from src.data.database import DB_PATH, _utc_now, list_companies
    from src.utils.config import WEB_DATA_CONFIG
    from src.utils.logging import get_logger

    log = get_logger(__name__)
    if file_path.exists():
        # Never replace a file a load may already have used — its uuids are the stored ids.
        print(f"Refusing: {file_path} already exists")
        return 2
    vt = WEB_DATA_CONFIG["data_types"]["VISIBLE_TEXT"]
    pl = WEB_DATA_CONFIG["data_types"]["PAGE_LINKS"]
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
        for key in WEB_DATA_CONFIG["company_data_id_keys"]:
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
            # pjl_assembled_content goes NULL only when rebuild-on-read gives today's text (AC 6 over AC 5).
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
        # pjl_nav_links was only ever a small temporary copy: dropped whatever it holds, rebuilt-or-not,
        # pages-or-not. Readers rebuild it from the page rows, or fall back to nav_links.
        if cd.get("pjl_nav_links") is not None:
            keys["pjl_nav_links"] = {"was": _digest(cd["pjl_nav_links"]), "value": None}

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
        _ensure_web_data_schema,
        _get_connection,
    )
    from src.utils.logging import get_logger

    log = get_logger(__name__)
    rows = json.loads(file_path.read_text())["rows"]
    # Raw INSERT, not save_web_data: that mints its own uuid, and the file's ids must be the
    # stored ids — that is what makes a re-run add nothing.
    conn = _get_connection()
    try:
        _ensure_web_data_schema(conn)
        log.debug("Calling INSERT OR IGNORE web_data: %s", list(rows))
        inserted = 0
        for rid, r in rows.items():
            cur = conn.execute(
                "INSERT OR IGNORE INTO web_data"
                " (web_data_id, candidate_id, url, data_type, content, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (rid, r["candidate_id"], r["url"], r["data_type"], _compress_payload(r["content"]), r["created_at"]),
            )
            inserted += cur.rowcount
        conn.commit()
        log.debug("Response from INSERT OR IGNORE web_data: inserted=%d", inserted)
    finally:
        conn.close()
    print(f"Rows in file: {len(rows)}  inserted: {inserted}  already present: {len(rows) - inserted}")
    return 0


def _clear(file_path: Path) -> int:
    from src.data.database import (
        get_company,
        get_web_data_for_ids,
        update_company,
    )
    from src.utils.logging import get_logger

    log = get_logger(__name__)
    companies = json.loads(file_path.read_text())["companies"]

    def _ids(value: Any) -> list[str]:
        # Row ids a new value points at: an id string, or list entries' id / links_id.
        if isinstance(value, str):
            return [value]
        return [e[k] for e in value or [] if isinstance(e, dict) for k in ("id", "links_id") if e.get(k)]

    wanted = {sn: [i for e in c["keys"].values() for i in _ids(e["value"])] for sn, c in companies.items()}
    all_ids = sorted({i for ids in wanted.values() for i in ids})
    log.debug("Calling get_web_data_for_ids: %s", all_ids)
    present = get_web_data_for_ids(all_ids)
    log.debug("Response from get_web_data_for_ids: %s", present)
    missing = {sn: [i for i in ids if i not in present] for sn, ids in wanted.items()}
    missing = {sn: ids for sn, ids in missing.items() if ids}
    if missing:
        # Refuse before any company write — a swapped key whose row is gone would lose its text.
        for sn, ids in missing.items():
            log.warning("%s clear refused: web_data rows missing %s", sn, ids)
        print(f"Refused: {sum(map(len, missing.values()))} rows missing for {len(missing)} companies — run load first")
        return 1

    updated = swapped = left = 0
    for sn, c in companies.items():
        log.debug("Calling get_company: %s", sn)
        company = get_company(sn)
        log.debug("Response from get_company: %s", company)
        if not company:
            left += len(c["keys"])
            log.warning("%s clear skipped: company no longer exists", sn)
            continue
        cd = dict(company.get("company_data") or {})
        done = []
        for key, entry in c["keys"].items():
            # Swap only a key still holding what export saw — a re-scrape since then wins.
            if _digest(cd.get(key)) == entry["was"]:
                cd[key] = entry["value"]
                done.append(key)
            else:
                left += 1
                log.warning("%s %s: changed since export — left as is", sn, key)
        if not done:
            continue
        # Original updated_at: the move isn't company activity.
        log.debug("Calling update_company: [%s company_data=%s updated_at=%s]", sn, cd, company.get("updated_at"))
        rc = update_company(sn, company_data=cd, updated_at=company.get("updated_at"))
        log.debug("Response from update_company: %s", rc)
        updated += 1
        swapped += len(done)
        log.info("%s | company scrape cleared: keys %s (batch: -)", sn, ",".join(done))
    print(f"Companies updated: {updated}/{len(companies)}  keys swapped: {swapped}  left as is: {left}")
    return 0


def _write_chunks(out_dir: Path, order: int, table: str, rows: list[dict[str, Any]], chunk_bytes: int) -> tuple[int, int]:
    """Write rows as JSON arrays of column-keyed objects (the admin Copy Output upsert shape), each file
    about chunk_bytes (a single row bigger than that gets its own file). Returns (files, bytes)."""
    files = total = size = 0
    batch: list[str] = []

    def flush() -> None:
        nonlocal files, total, size, batch
        if not batch:
            return
        files += 1
        text = "[" + ",".join(batch) + "]"
        (out_dir / f"{order}_{table}_{files:03d}.json").write_text(text)
        total += len(text)
        batch, size = [], 0

    for row in rows:
        s = json.dumps(row, separators=(",", ":"))
        if batch and size + len(s) > chunk_bytes:
            flush()
        batch.append(s)
        size += len(s) + 1
    flush()
    return files, total


def _dump(file_path: Path, out_dir: Path, chunk_bytes: int) -> int:
    from src.data.database import _get_connection
    from src.utils.logging import get_logger

    log = get_logger(__name__)
    if out_dir.exists() and any(out_dir.iterdir()):
        # Never mix chunks from two runs in one folder — the paste order would be wrong.
        print(f"Refusing: {out_dir} is not empty")
        return 2
    data = json.loads(file_path.read_text())
    companies: dict[str, Any] = data["companies"]
    # web_data rows straight from the export file: the same ids/content that load inserted.
    tele = [{"web_data_id": rid, **r} for rid, r in data["rows"].items()]
    company_rows: list[dict[str, Any]] = []
    not_cleared: list[str] = []
    conn = _get_connection()
    try:
        for sn, c in companies.items():
            cur = conn.execute("SELECT * FROM company WHERE short_name = ?", (sn,))
            fetched = cur.fetchone()
            if fetched is None:
                continue  # deleted since export; clear skips it too
            row = dict(zip([d[0] for d in cur.description], tuple(fetched)))
            cd = json.loads(row["company_data"] or "{}")
            # A key still holding what export saw means clear hasn't run — dumping now would push legacy text.
            # (A key changed since export is fine: clear leaves it, and the re-scrape wins.)
            if any(_digest(cd.get(k)) == e["was"] for k, e in c["keys"].items()):
                not_cleared.append(sn)
            company_rows.append(row)
    finally:
        conn.close()
    if not_cleared:
        log.warning("dump refused: company_data not in the cleared state for %s", not_cleared[:20])
        print(f"Refused: {len(not_cleared)} companies are not in the cleared state — run clear first")
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    tf, tb = _write_chunks(out_dir, 1, "web_data", tele, chunk_bytes)
    cf, cb = _write_chunks(out_dir, 2, "company", company_rows, chunk_bytes)
    print(f"web_data: {len(tele)} rows in {tf} files ({tb / 1e6:.1f} MB)")
    print(f"company: {len(company_rows)} rows in {cf} files ({cb / 1e6:.1f} MB)")
    print(f"Wrote {out_dir} — upsert the 1_web_data files first, then the 2_company files")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Move company scrape text into web_data (AST-2135).")
    parser.add_argument("mode", choices=("export", "load", "clear", "dump"))
    parser.add_argument("--file", required=True, help="Export JSON path (written by export, read by load/clear/dump).")
    parser.add_argument("--db-dir", help="Folder holding astral.db; defaults to the app's ASTRAL_DB_DIR.")
    parser.add_argument("--out-dir", help="dump only: folder for the chunked JSON files (must be empty or new).")
    parser.add_argument("--chunk-mb", type=float, default=4.0, help="dump only: approximate size of each file (default 4).")
    args = parser.parse_args()
    if args.db_dir:
        # Must be set before any src import: config reads ASTRAL_DB_DIR at import time and the
        # logger writes app_log into that same DB.
        os.environ["ASTRAL_DB_DIR"] = str(Path(args.db_dir).resolve())
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.data.database import DB_PATH

    print(f"DB: {DB_PATH}")
    file_path = Path(args.file)
    if args.mode == "dump":
        if not args.out_dir:
            parser.error("dump needs --out-dir")
        return _dump(file_path, Path(args.out_dir), int(args.chunk_mb * 1_000_000))
    return {"export": _export, "load": _load, "clear": _clear}[args.mode](file_path)


if __name__ == "__main__":
    sys.exit(main())

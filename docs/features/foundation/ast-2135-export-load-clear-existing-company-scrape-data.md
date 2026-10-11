# AST-2135 — Export / load / clear existing company scrape data

**Parent:** [AST-2130 — Create a new table telescope_data](https://linear.app/astralcareermatch/issue/AST-2130)
**Ticket:** [AST-2135](https://linear.app/astralcareermatch/issue/AST-2135)
**Publish ref:** `origin/sub/AST-2130/AST-2135-company-scrape-migration`

One new migration script moves the page text already sitting in existing `company_data` blobs into `telescope_data`, in three separately-run modes. **export** reads every company and writes a JSON file of telescope rows (pre-assigned uuids) plus, per company, the id-shaped value each scraped key should hold — no DB writes. **load** inserts the file's rows by uuid (`INSERT OR IGNORE`, so a second run adds 0). **clear** refuses (exit 1, no company writes) unless every row id the file references exists, then swaps each key to its id value. Every swap is chosen so AST-2134's resolve helpers return byte-identical text afterwards (AC 6 / AC 11); a key whose current value no longer matches what was exported, or a derived PJL field whose rebuild-on-read would differ, is left as-is with a warning rather than changed. Jobs are not touched.

## Scope check

This ticket's `## Scope` names one file: `scripts/migrations/migrate_company_scrape_to_telescope_data.py` (new; export / load / clear). Every stage edits only that file (plus this doc). Not edited: `database.py` / `config.py` (AST-2131), `gazer.py` (AST-2132), `tracker.py` (AST-2133), `roster.py` / `api_admin.py` (AST-2134), tests / bible (Betty). The script **calls** existing functions in `database.py` and `roster.py`; it changes none of them.

## Canon

`stat.logging.debug`, `stat.logging.warning`, `stat.logging.info.entity`. Consequences for this script:

- **debug:** every call into the data layer / roster helpers logs `Calling <fn>: [...]` and `Response from <fn>: ...` at `logger.debug` with full values — no truncation, no `if debug` gate.
- **warning:** one `logger.warning` line per item not migrated or blocked, naming the company, the key, and why (unexpected shape, value changed since export, derived field kept, referenced row missing).
- **info.entity:** one line per company per mode, `"%s | company %s: %s (batch: %s)"` — e.g. `acme | company scrape exported: 7 rows, keys homepage_text,nav_links,pjl_scrape_pages (batch: -)`. Batch is `-` (the script runs outside a dispatch batch; `log_batch_id` is unset), same as roster's `_entity_info`.
- The end-of-run totals are `print()`ed to stdout, like the other `scripts/migrations/*` scripts (`backfill_collapse_blank_lines.py` `_print_section`); they are not log lines.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `scripts/migrations/migrate_company_scrape_to_telescope_data.py` | New. CLI (`export` / `load` / `clear`, `--file`, `--db-dir`); export builds rows + per-company id values; load inserts rows by uuid; clear verifies rows then swaps keys | scripts |

## Background the builder needs (read, don't change)

- `company.company_data` is plain JSON TEXT; `list_companies()` / `get_company()` return it parsed; `update_company(short_name, company_data=..., updated_at=...)` re-serializes it and sets `updated_at` to now **unless** `updated_at` is passed.
- `DB_PATH` is `ASTRAL_CONFIG["db_dir"] / "astral.db"`, where `db_dir` comes from `os.environ["ASTRAL_DB_DIR"]` **at import of `src.utils.config`**. The logger's `app_log` sink writes to that same DB.
- `telescope_data` content is `_compress_payload(text)` (zlib of the utf-8 string); `_ensure_telescope_data_schema(conn)` creates the table idempotently; `get_telescope_data_for_ids(ids) -> {id: content}`.
- `TELESCOPE_DATA_CONFIG["data_types"]` → `VISIBLE_TEXT`, `PAGE_LINKS`; `TELESCOPE_DATA_CONFIG["company_data_id_keys"]` → `homepage_text`, `nav_links`, `website_content`, `job_list_visible`, `pjl_scrape_pages`.
- Legacy shapes (writers on `origin/dev` before this epic): `homepage_text` / `job_list_visible` = visible-text string; `nav_links` = enumerated links string; `website_content` = `[{url, content}]` (content stripped) or, older, a plain string; `pjl_scrape_pages` = `[{url, visible_text, enumerated_nav_links?}]` (text non-blank, both stripped); `pjl_assembled_content` / `pjl_nav_links` = stored strings.
- Readers after AST-2134 (`roster._resolve_company_value`, `_resolved_pjl_pages`, `_resolved_company_data`, `_pjl_maps_from_company_data`): an id string resolves to the row content verbatim; a `website_content` list entry `{url, id}` resolves to `{url, content}` (content stripped); a `pjl_scrape_pages` entry `{url, id, links_id?}` resolves to `{url, visible_text, enumerated_nav_links?}` (both stripped, links omitted when blank); entries without an id pass through; `pjl_nav_links` is rebuilt only when it is `None`; `pjl_assembled_content` is rebuilt only when it is empty.
- The worktree's local DB currently has **0 companies** (checked on a copy), so all verification runs on synthetic legacy companies seeded into a temp copy (see **Verification**).

## ⛔ Live DB guard (every stage, every run)

- `data/astral.db` in this worktree is a symlink to Susan's live `~/astral/data/astral.db`. **Never** run the script, the scratch checks, or anything that imports `src.*` with `ASTRAL_DB_DIR` pointing at `data/` or `~/astral/data/`.
- Every run in this pipeline is `--db-dir /tmp/AST-2135` against a copy made with `cp`:
  `mkdir -p /tmp/AST-2135 && cp -L data/astral.db /tmp/AST-2135/astral.db` (+ `-wal` / `-shm` from `~/astral/data/` if present). The file **must** be named `astral.db` inside that dir — the app derives `DB_PATH` from the directory.
- Shell exports for every command: `export ASTRAL_DB_DIR=/tmp/AST-2135` **and** pass `--db-dir /tmp/AST-2135`. If any step would write to `data/astral.db`, stop and post 🛑.
- The real migration (export → load → clear against the app DB) is Susan's to run after UAT. This plan never runs it.

## Stage 0: Drift check (no commit)

**Done when:** every item below holds on HEAD after `sync-child.sh`, or the builder has stopped and posted 🛑 on AST-2135.

1. `src/data/database.py` exports `_get_connection`, `_compress_payload`, `_ensure_telescope_data_schema`, `_utc_now`, `list_companies`, `get_company`, `update_company` (allowlist includes `company_data` and `updated_at`), `get_telescope_data_for_ids`.
2. `src/core/roster.py` defines `_assemble_pjl_content(pages)`, `_rebuilt_pjl_nav_links(cdata)`, `_resolved_company_data(cdata)` with the behavior in **Background**.
3. `src/core/gazer.py` defines `is_telescope_id(value)`.
4. `src/utils/config.py` `TELESCOPE_DATA_CONFIG` has the `data_types` / `company_data_id_keys` above.
5. `src/ui/api/api_admin.py` defines `_build_adhoc_live_content(task_key, entity_id, entity_ids=None)` (used only by the scratch verification).

## Stage 1: Script skeleton, DB pinning, export

**Done when:** `export` on the seeded temp DB writes the JSON file described below; the AC 10 export check (company dump + `telescope_data` count unchanged) passes; lint/compile gate passes.

1. Create `scripts/migrations/migrate_company_scrape_to_telescope_data.py` with a module docstring in the house style (what it does, the three modes, usage lines including `--db-dir`, and the sentence "Run export → load → clear in that order; clear refuses while any referenced row is missing.").
2. **DB pinning before any `src` import.** Parse args first with `argparse` (subcommand-free: positional `mode` in `{"export","load","clear"}`, `--file PATH` required, `--db-dir DIR` optional). If `--db-dir` is given, set `os.environ["ASTRAL_DB_DIR"] = str(Path(args.db_dir).resolve())`; then `sys.path.insert(...)` and import `src.*` (imports live inside `main()` after this, with a comment saying why: config reads `ASTRAL_DB_DIR` at import and the logger writes `app_log` to that DB).
   ⚠️ **Decision:** `--db-dir` is optional; without it the script uses the app's `ASTRAL_DB_DIR` (Susan's real run). This matches the ticket's MIGRATION GUARD ("a DB path it is given explicitly or the app DB only when run by Susan"). The script never guesses a path and never defaults to `data/`. First output line of every mode is `print(f"DB: {DB_PATH}")` so the target is visible before anything happens.
3. **Export** — `_export(file_path)`:
   - `list_companies()` (all, no filters; debug Calling/Response).
   - Build `rows: dict[str, dict]` keyed by the new `telescope_data_id` (`str(uuid.uuid4())`) and `companies: dict[str, dict]` keyed by `short_name`. One `created_at = _utc_now()` for the run.
   - A helper `_new_row(rows, candidate_id, url, data_type, content) -> str` adds `{candidate_id, url, data_type, content, created_at}` under a new uuid and returns the uuid. `content` is stored verbatim (no strip — legacy values are already in reader shape).
   - Per company: `cid = company.get("candidate_id")`; `site = (company.get("company_website") or company.get("job_site") or "").strip()` (same URL roster's homepage writers record); `job_url = (company.get("job_site") or site).strip()`.
   - Per key in `company_data_id_keys` with value `v` (skip `None`):
     - **`homepage_text`, `job_list_visible`** — non-blank `str`, not `is_telescope_id` → id value `_new_row(..., url=site or job_url, VISIBLE_TEXT, v)`.
     - **`nav_links`** — same rule, `PAGE_LINKS`, url `site`.
     - **`website_content`** — non-blank `str` (oldest shape) → single id (`VISIBLE_TEXT`, url `site`). `list` → map entries: an entry whose keys are exactly `{"url","content"}` with non-blank content → `{"url": e["url"], "id": _new_row(..., e["url"], VISIBLE_TEXT, e["content"])}`; any other entry (already `{url, id}`, blank content, other keys) is kept as-is. Key order `url` then `content` is what the resolver reproduces, so the round-trip is identical.
     - **`pjl_scrape_pages`** — `list`; an entry whose keys are a subset of `{"url","visible_text","enumerated_nav_links"}` with non-blank `visible_text` → `{"url", "id": VISIBLE_TEXT row, "links_id": PAGE_LINKS row}` (omit `links_id` when `enumerated_nav_links` is blank/absent); others kept as-is.
     - Blank strings and values that are already ids / already id-shaped lists produce nothing (debug line only). Any other type (dict, number, list entry that is not a dict, entry with extra keys) is kept as-is with **one warning per company+key**: `"<short_name> website_content: 2 entries not migrated (unexpected keys) — left as text"`.
     - A key is recorded only when its new value differs from the old: `companies[sn]["keys"][key] = {"was": _digest(v), "value": new_value}` where `_digest(v) = sha256(json.dumps(v, sort_keys=True))` hexdigest.
     ⚠️ **Decision:** the `was` digest lets clear skip a key that changed between export and clear (a re-scrape in between would otherwise be overwritten with older text's id). Cheap and only ever makes clear do *less*. Flagged for Joan/Susan; strike it if unwanted.
   - **Derived PJL fields** (only when `pjl_scrape_pages` was recorded for this company, using the company's *legacy* blob): with `pages = cd["pjl_scrape_pages"]`,
     - `pjl_assembled_content` (if not `None`): safe to null iff `cd["pjl_assembled_content"].strip() == "" or cd["pjl_assembled_content"].strip() == roster._assemble_pjl_content(pages)` (its only reader strips and falls back to assembling the pages).
     - `pjl_nav_links` (if not `None`): safe to null iff `cd["pjl_nav_links"] == roster._rebuilt_pjl_nav_links(cd)` (exact — one reader uses it unstripped).
     - Safe → `companies[sn]["keys"][field] = {"was": _digest(old), "value": None}`. Not safe → warning `"<sn> pjl_nav_links: stored text differs from rebuild — left stored"` and no entry.
     ⚠️ **Decision (AC 5 vs AC 6):** AC 5 wants these fields NULL; AC 6 / AC 11 want byte-identical reader output. Where the rebuild would differ, this keeps the stored text (AC 6 wins) and says so per company; AST-2134 argued the two are always equal, so the expectation is zero such warnings. Flagged.
   - Per company with any recorded key: info entity line `"<sn> | company scrape exported: <n> rows, keys <k1,k2…> (batch: -)"`.
   - Write `{"exported_at": created_at, "db_path": str(DB_PATH), "rows": rows, "companies": companies}` to `--file` with `json.dump(..., indent=2)`; refuse (exit 2, nothing written) if `--file` already exists, so an export can't silently replace the file a load already used.
   - `print` totals: companies scanned / with changes, rows by data type, warnings.
4. Export performs no `company` / `telescope_data` writes. (`list_companies` runs the schema-ensure no-ops, and log lines land in `app_log` — neither touches the two things AC 10 checks.)

## Stage 2: Load

**Done when:** on the seeded temp DB after Stage 1's export, `load` inserts `len(rows)` rows; a second `load` prints `inserted 0`; each loaded row reads back through `get_telescope_data_for_ids` as the file's content; lint/compile gate passes.

1. `_load(file_path)`: read the file; `conn = _get_connection()`; `_ensure_telescope_data_schema(conn)`; for each `rid, r in rows.items()`: `INSERT OR IGNORE INTO telescope_data (telescope_data_id, candidate_id, url, data_type, content, created_at) VALUES (?,?,?,?,?,?)` with `_compress_payload(r["content"])`; sum `cursor.rowcount` as inserted; one `conn.commit()`; close in `finally`.
   ⚠️ **Decision:** raw `INSERT OR IGNORE` on `_get_connection()` instead of `save_telescope_data`, because that function mints its own uuid and the file's ids must be the stored ids (that is what makes re-runs add nothing). Same private-helper use as `backfill_collapse_blank_lines.py`. No change to `database.py`.
2. Debug Calling/Response around the insert loop (row ids in, inserted count out). Info entity line per company is not emitted here (rows aren't per-company-keyed in the loop); `print` `inserted N, already present M`.

## Stage 3: Clear

**Done when:** on the seeded temp DB — (a) `clear` against a fresh copy with an empty `telescope_data` exits 1 and the company dump is unchanged; (b) after `load`, `clear` exits 0, every migrated key is id-shaped, derived fields are NULL where recorded, and **Verification** shows identical reader output; (c) a second `clear` changes nothing (all keys' `was` digests now mismatch → skipped with warnings, or nothing to do); lint/compile gate passes.

1. `_clear(file_path)`: read the file. Collect every referenced id from `companies[*]["keys"][*]["value"]` (id strings; list entries' `id` and `links_id`). `get_telescope_data_for_ids(all_ids)` (debug Calling/Response).
2. **Refuse:** if any id is missing, one warning per company listing its missing ids (`"<sn> clear refused: telescope_data rows missing [..]"`), `print` the total, `sys.exit(1)` — before any `update_company` call.
3. Otherwise per company: `get_company(sn)` (warn + skip if gone); `cd = dict(company["company_data"])`; for each recorded key: if `_digest(cd.get(key)) == entry["was"]` → `cd[key] = entry["value"]`, else warning `"<sn> <key>: changed since export — left as is"`. If anything changed: `update_company(sn, company_data=cd, updated_at=company["updated_at"])` (debug Calling/Response) and info entity line `"<sn> | company scrape cleared: keys <…> (batch: -)"`.
   ⚠️ **Decision:** pass the original `updated_at` so the migration doesn't make every company look freshly touched (lists sorted by `updated_at` stay as they were). Flagged.
4. `print` totals: companies updated / skipped, keys swapped / left, warnings. Exit 0.

## Verification (scratch, temp DB only — no commit)

Scratch files live in `/tmp/AST-2135/` (never committed, never under `debug/`). All commands run with `export ASTRAL_DB_DIR=/tmp/AST-2135` and `--db-dir /tmp/AST-2135`. Python: `~/astral/.venv/bin/python`.

1. **Seed** (`/tmp/AST-2135/seed.py`): on the temp copy, `save_company`/`update_company` four synthetic companies (candidate_id = an existing candidate on the copy, `company_website` set, state `PJL_READY`) covering: (a) homepage_text + nav_links + job_list_visible strings + `website_content` `[{url, content}]` ×2; (b) `website_content` legacy plain string + a blank `homepage_text`; (c) `pjl_scrape_pages` with 2 pages (one with `enumerated_nav_links`, one without) + `possible_joblist_links` for both + `pjl_assembled_content` = `_assemble_pjl_content(pages)` + `pjl_nav_links` = `_rebuilt_pjl_nav_links(cd)`; (d) like (c) but `pjl_nav_links` hand-edited so it differs from the rebuild (expect "left stored" warning).
2. **Before snapshot** (`/tmp/AST-2135/snap.py before`): per company, `json.dumps(_resolved_company_data(cd), sort_keys=True)` and `_build_adhoc_live_content(t, sn)` for `t` in `prefilter_company`, `select_job_page`, `gaze`; plus `SELECT short_name, company_data FROM company` and `SELECT COUNT(*) FROM telescope_data` → `/tmp/AST-2135/before.json`.
3. **AC 10 export:** run `export --file /tmp/AST-2135/export.json`; re-dump company + count → identical to step 2's.
4. **AC 10 refuse:** copy the seeded DB to `/tmp/AST-2135-empty/astral.db`, `DELETE FROM telescope_data` there, run `clear --db-dir /tmp/AST-2135-empty --file /tmp/AST-2135/export.json` → exit 1, company dump unchanged.
5. **AC 10 load twice:** `load` → inserted = row count; `load` again → `inserted 0`.
6. **Clear + AC 5/6/11:** `clear` → exit 0. Re-run `snap.py after` → resolved blobs and all three admin previews byte-identical to before for every company; raw blobs: migrated keys id-shaped (`is_telescope_id` / `{url, id[, links_id]}`), `pjl_assembled_content` / `pjl_nav_links` NULL for (c), `pjl_nav_links` still stored for (d); `updated_at` unchanged.
7. **Re-run clear** → no `update_company` calls.

Report the outputs in the `## Review` section build-child writes.

## Lint / compile gate (every stage commit)

- `~/astral/.venv/bin/python -m py_compile scripts/migrations/migrate_company_scrape_to_telescope_data.py`
- `~/astral/.venv/bin/ruff check scripts/migrations/migrate_company_scrape_to_telescope_data.py` — clean (use `str | None`, `dict`, `list`, not `typing.Optional` / `Dict`).
- Commits: `code(AST-2135): …` one per stage, pushed to `origin/sub/AST-2130/AST-2135-company-scrape-migration` after each.

## Boundaries

No writer / reader changes; jobs untouched; no `database.py` / `roster.py` / `config.py` edits; no runs against `data/astral.db` or `~/astral/data/astral.db`; the 113 pre-existing stray `telescope_data` rows in the live DB (AST-2132 build) are not this script's concern — they are not referenced by any company and export/load/clear neither read nor delete them.

## Flags for Chuckles / Archie (not acted on)

1. **Digest guard** (Stage 1 step 3) — skips keys changed between export and clear. Strike if unwanted.
2. **Derived-field keep-on-mismatch** (Stage 1) — AC 6 wins over AC 5 for any company whose stored `pjl_nav_links` / `pjl_assembled_content` differ from the rebuild; each one is warned. Expected count: 0.
3. **Original `updated_at` preserved** on clear.
4. **Run on Railway:** the real data lives where Susan's app runs (the local DB has no companies). Susan's run: `python scripts/migrations/migrate_company_scrape_to_telescope_data.py export --file <path>` then `load`, then `clear`, all with that host's `ASTRAL_DB_DIR`; keep the export file until after clear.

## Estimate

Confirm Chuckles estimate: 3 — agree.

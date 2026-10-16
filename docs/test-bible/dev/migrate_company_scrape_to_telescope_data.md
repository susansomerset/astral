# migrate_company_scrape_to_telescope_data (migration script)

**Test module:** `tests/component/scripts/test_migrate_company_scrape_to_telescope_data.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `scripts/migrations/migrate_company_scrape_to_telescope_data.py` | `tests/component/scripts/test_migrate_company_scrape_to_telescope_data.py` | no |

**Table under it:** `docs/test-bible/data/database/telescope_data.md` (**AST-2131**). **Readers it must keep byte-identical:** `docs/test-bible/core/roster.md` + `docs/test-bible/ui/api/api_admin.md` (**AST-2134**).

---

### AST-2135 · AST-2130

**Publish:** `origin/sub/AST-2130/AST-2135-company-scrape-migration`. Plan: `docs/features/foundation/ast-2135-export-load-clear-existing-company-scrape-data.md`.

One-time operator script, three separately-run modes: **export** (company blobs → JSON file of pre-uuid'd telescope rows + per-company target values with a `was` digest; no DB writes), **load** (`INSERT OR IGNORE` by uuid), **clear** (refuse unless every referenced id exists; swap only keys whose digest still matches; preserve `updated_at`). `--db-dir` sets `ASTRAL_DB_DIR` before any `src` import; `DB: <path>` is always the first line printed.

**Isolation (hard rule):** every test builds its own DB under `tmp_path` (`ASTRAL_DB_DIR` + `database.DB_PATH` patched, process-global `_*_ensured` / `_*_applied` schema flags reset, buffered `app_log` flushed before teardown). The CLI test points `ASTRAL_DB_DIR` at a decoy dir and asserts `--db-dir` wins (decoy gets no `company` / `web_data` table). Running the module with `ASTRAL_DB_DIR=<empty tmp dir>` leaves that dir empty.

**`pjl_nav_links` is dropped, not migrated:** export sets any stored value to NULL (matching the rebuild or not, with pages or not) — it was only ever a small temporary copy, so nothing moves to `web_data` for it. Readers rebuild it from the page rows or fall back to `nav_links`. `pjl_assembled_content` keeps its rule: NULL only when it equals the rebuild, otherwise left stored and warned.

**Seed (`_seed`)** — seven companies covering every export branch: **acme** (legacy text in every key, 2 PJL pages one with links, derived fields equal to their rebuild, `job_site`), **beta** (plain-string `website_content`, assembled text that does *not* match the rebuild → kept + warned; stale `pjl_nav_links` → dropped), **gamma** (already ids), **delta** (odd shapes — warned, left alone), **empty**, **epsilon** (PJL pages with no stored derived fields + one extra-key page left as text), **zeta** (`pjl_nav_links` text and no pages → only the nav drop).

| Area | Source | Component tests |
| --- | --- | --- |
| AC10 — export writes the file, `company` + `web_data` unchanged, `DB:` path, only companies with movable text listed, scan/changes summary | `_export` | `TestAst2135Export::test_ac10_export_writes_file_and_no_db_change` |
| Export refuses an existing `--file` (exit 2) | `_export` | `TestAst2135Export::test_export_refuses_existing_file` |
| Row shapes per key (VISIBLE_TEXT / PAGE_LINKS, `job_site` URL, `{url, id[, links_id]}`), `pjl_assembled_content` → `None` only on rebuild match (mismatch warned), `pjl_nav_links` → `None` always, odd shapes warned (`Warnings: 4`) | `_export` | `TestAst2135Export::test_export_rows_and_target_values` |
| AC10 — load twice: all rows in, second run inserts 0; content round-trips | `_load` | `TestAst2135LoadClear::test_ac10_load_twice_adds_nothing_second_time` |
| AC10 — clear on empty `web_data` → exit 1, no company writes | `_clear` | `TestAst2135LoadClear::test_ac10_clear_refuses_on_empty_web_data` |
| Clear refuses when any single referenced row is missing | `_clear` | `TestAst2135LoadClear::test_clear_refuses_when_any_row_missing` |
| AC5 / AC6 / AC11 — after load + clear, resolved reader view (`_resolved_company_data` + `_pjl_maps_from_company_data`) and admin previews (`prefilter_company` / `select_job_page` / `gaze`) byte-identical for every company, except the dropped `pjl_nav_links` (beta, zeta: view's nav list now empty; only `select_job_page` may differ, `prefilter_company` / `gaze` still identical); raw blobs id-shaped, matched assembled text and every `pjl_nav_links` NULL; `updated_at` preserved; untouched companies identical | `_clear` + AST-2134 readers | `TestAst2135LoadClear::test_ac5_ac6_ac11_after_load_and_clear` |
| Key changed since export → left as is (digest guard) | `_clear` | `TestAst2135LoadClear::test_clear_leaves_keys_changed_since_export` |
| Clear rerun is a no-op; deleted company skipped | `_clear` | `TestAst2135LoadClear::test_clear_rerun_and_deleted_company` |
| `main()` prints `DB:` first, with and without `--db-dir`, and dispatches | `main` | `TestAst2135Cli::test_main_prints_db_path_then_dispatches` |
| Subprocess export → load → clear pinned to `--db-dir` over a decoy `ASTRAL_DB_DIR` | `main` / `__main__` | `TestAst2135Cli::test_db_dir_pins_every_mode_to_the_given_folder` |

| `dump` refuses before `clear` (exit 1, no files); refuses a non-empty `--out-dir` (exit 2) | `_dump` | `TestAst2135Dump::test_dump_refuses_before_clear_and_writes_nothing`, `::test_dump_refuses_non_empty_out_dir` |
| `dump` chunks in paste order (`1_web_data_*` then `2_company_*`), every file row once, company rows raw with `company_data` as stored text | `_dump` / `_write_chunks` | `TestAst2135Dump::test_dump_chunks_in_paste_order` |
| `dump` files round-trip through the real Copy Output upsert (`apply_copy_output_table_upsert`): all telescope rows inserted, stale company blobs replaced, content reads back verbatim | `_dump` + `table_copy_upsert` | `TestAst2135Dump::test_dump_files_round_trip_through_the_copy_output_upsert` |
| `dump` accepts a key re-scraped since export; skips a company deleted since export; an empty export writes no files; `main` needs `--out-dir` | `_dump` / `main` | `TestAst2135Dump::test_dump_accepts_a_key_changed_since_export`, `::test_dump_skips_a_company_deleted_since_export`, `::test_dump_of_an_empty_export_writes_no_files`, `::test_main_dump_needs_out_dir` |

**Upsert stores plain text:** the Copy Output route writes `web_data.content` as plain `text`, where `load` stores it compressed (like `agent_data`). Reads are identical (`get_web_data_for_ids`); on the prod-sized rehearsal that was 194 MB vs 53 MB on disk.

**Coverage:** 99% branch on the script in-process (only the `if __name__ == "__main__"` line, which the subprocess test runs). Measure with `--cov=scripts/migrations --cov-branch` (the harness report only tracks `src/`).

**Plan flags (tested as written):** derived-field rule — AC6 wins over AC5 on mismatch for `pjl_assembled_content` (beta: stored text kept, warned); **`pjl_nav_links` is the exception — always dropped (Susan, post-UAT: temporary storage, not worth keeping or migrating; AC6 deliberately does not hold for it)**; `was` digest guard; `updated_at` pass-through.

**Real-data note:** a read-only backup of the live sqlite DB has 0 companies (113 `web_data` rows), so an AC6 rehearsal on real companies is moot; CLI export/load/clear on that temp copy exited 0 with 0 companies. The real migration is Susan's to run after UAT.

**Broken / obsolete:** none — the product diff is the new script + plan doc only.

**Integration:** none.

## QA test manifest — AST-2135

1. `ASTRAL_DB_DIR=<empty tmp dir> ./scripts/testing/run_component_tests.sh tests/component/scripts/test_migrate_company_scrape_to_telescope_data.py -q` — 19 passed; the tmp dir stays empty.
2. No-regression: `tests/component/scripts` failure set equals the ftr baseline (11 pre-existing failures: 8 `test_cleanup_duplicate_and_board_gaze_jobs.py`, 2 `test_record_landed_parent.py`, 1 `test_backfill_agent_data_refs.py`; none in this module).
3. Live DB untouched: `web_data` row count in `~/astral/data/astral.db` (read-only `mode=ro`) is the same before and after items 1–2. Never run `load` / `clear` against `data/astral.db`.

**Pass criterion:** items 1–3 — narrowed run, not the zero-arg harness / branch-lock gate (pre-existing reds on the ftr tip).

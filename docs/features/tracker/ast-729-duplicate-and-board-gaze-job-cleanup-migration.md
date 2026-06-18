# Duplicate and board-gaze job cleanup migration (Duplicate jobs ingested)

**Linear issue:** https://linear.app/astralcareermatch/issue/AST-729/duplicate-and-board-gaze-job-cleanup-migration-duplicate-jobs-ingested

**Publish ref:** `sub/AST-728/AST-729-duplicate-and-board-gaze-job-cleanup-migration`

One-time operator-run migration script that cleans existing bad `job` rows before **AST-732** adds the unique identity index. Phase 1 removes all jobs under decommissioned board-gaze placeholder companies (`__board__*`). Phase 2 deduplicates remaining jobs that share the same `(company, job_title, company_job_id)` triple, keeping the row with minimum `created_at` (ties broken by minimum `astral_job_id`). Related records for deleted `astral_job_id` values are left as-is per ticket boundaries.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `scripts/migrations/migrate_job_identity_cleanup.py` | New operator migration script | script |

## Stage 1: Migration script — board cleanup + identity dedupe

**Done when:** `scripts/migrations/migrate_job_identity_cleanup.py` exists, runs with `--dry-run` without writing, and with live mode performs board cleanup then identity dedupe using direct SQLite against `ASTRAL_CONFIG["db_dir"] / "astral.db"`. No changes to `src/data/database.py` or runtime Tracker/Gazer/Consult code.

1. Create `scripts/migrations/migrate_job_identity_cleanup.py` with the standard migration preamble: shebang, module docstring (operator runbook — see Stage 2), `sys.path.insert(0, …)` to repo root (same as `backfill_collapse_blank_lines.py`).
2. Imports: `argparse`, `sqlite3`, `sys`, `Path`, `Dict`, `Optional`, `Tuple` from typing; `ASTRAL_CONFIG` and `BOARDS_CONFIG` from `src.utils.config`.
3. Define module constants:
   - `DB_PATH = ASTRAL_CONFIG["db_dir"] / "astral.db"`
   - `_BOARD_PREFIX = BOARDS_CONFIG["ingest"]["placeholder_company_prefix"]` (must resolve to `"__board__"`)
   - `_COUNT_KEYS = ("scanned", "deleted", "unchanged", "errors")`
4. Add `_conn() -> sqlite3.Connection` opening `DB_PATH` with `row_factory = sqlite3.Row` (same pattern as `migrate_agent_data.py`).
5. Add `_empty_counts() -> Dict[str, int]` returning zeroed `_COUNT_KEYS`.
6. Add `_print_section(label: str, counts: Dict[str, int]) -> None` printing `scanned/deleted/unchanged/errors` (mirror `backfill_collapse_blank_lines.py` summary style).
7. Implement `cleanup_board_gaze_jobs(conn: sqlite3.Connection, dry_run: bool) -> Dict[str, int]`:
   - Count rows: `SELECT COUNT(*) FROM job WHERE company LIKE ?` with bind `f"{_BOARD_PREFIX}%"`.
   - If count is 0: return counts with `unchanged` = scanned.
   - If `dry_run`: print one line per distinct `company` value matching the prefix (`SELECT DISTINCT company FROM job WHERE company LIKE ? ORDER BY company`) with `[board {company}] DRY RUN — would delete N job row(s)` where N is per-company count; increment `scanned` by total rows, `deleted` by total rows (preview only).
   - Else: `DELETE FROM job WHERE company LIKE ?` with same bind; `conn.commit()`; set `deleted` to `cursor.rowcount`, `scanned` to same.
   - Wrap in try/except per phase; on unexpected SQL failure print error and increment `errors`, do not partial-commit outside the single DELETE.
8. Implement `dedupe_identity_triples(conn: sqlite3.Connection, dry_run: bool) -> Dict[str, int]`:
   - **Scope:** only rows where `company_job_id IS NOT NULL AND job_title IS NOT NULL AND TRIM(company_job_id) != '' AND TRIM(job_title) != ''` and `company NOT LIKE ?` with `_BOARD_PREFIX + '%'` (board rows already removed in phase 1; this guard keeps phase 2 safe if run alone later).
   - **Survivor rule:** within each `(company, job_title, company_job_id)` group, keep the row with minimum `created_at` (ISO text sort matches existing timestamps). Tie-break: minimum `astral_job_id`.
   - **Selection SQL** (use as subquery; SQLite 3.25+ window functions available in project):
     ```sql
     SELECT astral_job_id, company, job_title, company_job_id, created_at
     FROM (
       SELECT astral_job_id, company, job_title, company_job_id, created_at,
              ROW_NUMBER() OVER (
                PARTITION BY company, job_title, company_job_id
                ORDER BY created_at ASC, astral_job_id ASC
              ) AS rn
       FROM job
       WHERE company_job_id IS NOT NULL
         AND job_title IS NOT NULL
         AND TRIM(company_job_id) != ''
         AND TRIM(job_title) != ''
         AND company NOT LIKE ?
     )
     WHERE rn > 1
     ```
   - Fetch all doomed `astral_job_id` values. `scanned` = number of duplicate rows to delete (not total jobs in DB).
   - If none: return with `unchanged` = 0, `scanned` = 0.
   - If `dry_run`: print `[dedupe {astral_job_id}] DRY RUN — would delete duplicate (company={company}, job_title={job_title!r}, company_job_id={company_job_id!r}, created_at={created_at})` for each row; set `deleted` = len(rows) for preview counts.
   - Else: delete in batches of 500 using `DELETE FROM job WHERE astral_job_id IN ({placeholders})` to avoid oversized IN lists; one `conn.commit()` after all batches; `deleted` = total rowcount.
9. Implement `run_migration(dry_run: bool = False, skip_board: bool = False, skip_dedupe: bool = False) -> None`:
   - Print `=== DRY RUN — no DB writes ===` header when `dry_run`.
   - Open connection in `try/finally` (always close).
   - Run board phase unless `skip_board`, then dedupe phase unless `skip_dedupe` (order is mandatory: board first, dedupe second).
   - Print `=== SUMMARY ===` (or dry-run variant) with `_print_section` for each phase executed.
10. `if __name__ == "__main__"`: `argparse` with:
    - `--dry-run` (store_true)
    - `--skip-board` (store_true, for operator re-run when board phase already done)
    - `--skip-dedupe` (store_true, for operator re-run when only board cleanup needed)
    - Call `run_migration(...)`.

⚠️ **Decision:** Script uses direct SQLite DELETE in the migration file rather than new `database.py` helpers. Ticket scope is operator migration only; `_remove_jobs_by_company` is the precedent for DELETE shape but is not imported (private API). Config prefix comes from `BOARDS_CONFIG["ingest"]["placeholder_company_prefix"]`, not a hardcoded string.

⚠️ **Decision:** Empty-string `company_job_id` / `job_title` are excluded from dedupe groups (treated like incomplete identity), consistent with NULL exclusion in AST-729 notes.

## Stage 2: Operator runbook in module docstring

**Done when:** The module docstring at the top of `migrate_job_identity_cleanup.py` documents purpose, phase order, dry-run usage, live run steps, idempotency, and dependency on running before AST-732 in each environment.

1. In the module docstring, include:
   - **Purpose:** one-time cleanup before unique index (**AST-732**).
   - **Phase order:** (1) delete all `__board__*` jobs, (2) dedupe identity triples on remainder.
   - **Usage examples:**
     ```
     python scripts/migrations/migrate_job_identity_cleanup.py --dry-run
     python scripts/migrations/migrate_job_identity_cleanup.py
     python scripts/migrations/migrate_job_identity_cleanup.py --skip-board   # dedupe only
     python scripts/migrations/migrate_job_identity_cleanup.py --skip-dedupe  # board only
     ```
   - **Operator checklist:** stop app workers or run during maintenance window; run `--dry-run` first and review counts/lines; back up `astral.db` before live run; run live without `--dry-run`; re-run `--dry-run` afterward — expect zero board rows and zero duplicate triples.
   - **Idempotency:** safe to re-run; second run should report `unchanged`/zero deletes if cleanup already applied.
   - **Out of scope:** does not touch agent_data, agent_responses, timesheets, or dispatch_ledger rows for deleted jobs.

## Stage 3: Compile gate

**Done when:** `python -m py_compile scripts/migrations/migrate_job_identity_cleanup.py` exits 0 on the epic worktree.

1. Run `python -m py_compile scripts/migrations/migrate_job_identity_cleanup.py` from repo root.
2. Fix any syntax/import errors before stage commit.

## Self-Assessment

**Scope:** `Single-Component` — one new file under `scripts/migrations/`; no runtime Tracker, Gazer, Consult, or data-layer API changes.

**Conf:** `high` — survivor rule, board prefix, NULL/empty identity exclusion, and phase order are fully specified in AST-729/AST-728; script follows existing migration patterns (`backfill_collapse_blank_lines.py`, `migrate_agent_data.py` connection style).

**Risk:** `Medium` — incorrect survivor selection deletes the wrong pipeline row for an identity triple (orphaned related rows remain by design); mitigated by `--dry-run`, deterministic `ORDER BY created_at ASC, astral_job_id ASC`, and excluding incomplete identity triples.

## ASTRAL_CODE_RULES self-review

- **§1.3 DRY:** Shared `_empty_counts`, `_print_section`, single `_conn()` — no duplicate connection boilerplate.
- **§2.1 Config:** Board prefix from `BOARDS_CONFIG`, DB path from `ASTRAL_CONFIG` — no hardcoded magic strings for prefix or path.
- **§2.4 Batch processing:** N/A — not a dispatch batch task.
- **§3.3 Imports:** Script imports only `src.utils.config` (allowed); no core/ui imports.
- **§3.5 Naming:** snake_case throughout; migration filename describes purpose.
- **No conflicts** requiring plan revision.

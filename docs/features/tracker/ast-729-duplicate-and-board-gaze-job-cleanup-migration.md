# Duplicate and board-gaze job cleanup migration (Duplicate jobs ingested)

**Linear:** [AST-729](https://linear.app/astralcareermatch/issue/AST-729/duplicate-and-board-gaze-job-cleanup-migration-duplicate-jobs-ingested)  
**Parent:** [AST-728](https://linear.app/astralcareermatch/issue/AST-728/duplicate-jobs-ingested) (context only — unique index is **AST-732**; post-qualify collision delete is **AST-733**)  
**Publish ref:** `sub/AST-728/AST-729-duplicate-board-gaze-cleanup-migration`

**Summary:** Ship a one-time operator-run CLI migration that removes legacy bad job rows before the unique identity index lands: (1) for each duplicate group sharing the same `(company, job_title, company_job_id)` triple among real (non-board) companies, keep the row with the earliest `created_at` and delete the rest; (2) delete every job row whose `company` is a board-gaze placeholder (`__board__*`). Related records (`agent_data`, `agent_responses`, timesheets, `dispatch_ledger`) for deleted jobs are **left as-is** — no re-pointing, no cascade deletes.

**Out of scope:** Unique index or insert-time duplicate tolerance (**AST-732**); post–`qualify_job_listings` collision delete path (**AST-733**); deleting or re-pointing related records; UI; runtime ingest/dedup logic changes; dedupe groups where any identity column is NULL or empty (pre-Consult rows).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py` | New one-time cleanup CLI | scripts |

**No `src/` product changes in this ticket** — migration uses existing private database helpers (`_get_connection`, `_ensure_job_schema`, `_run_with_retry`) for reads/writes, same precedent as `backfill_latest_only_rubric_entity_data.py`.

**No test edits in this ticket** — Betty owns manifest + bible at **qa-child**.

Spike output (if needed): **`debug/spikes/AST-729/…`** only — not repo root `artifacts/`.

---

## Stage 1: Migration script

**Done when:** Script runs with `--dry-run` against a copy of prod-shaped DB, prints per-group/per-delete actions and summary counts, and with live flags deletes only targeted `job` rows; `SELECT COUNT(*) FROM agent_data` unchanged before/after.

1. Create **`scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py`** following **`scripts/migrations/backfill_collapse_blank_lines.py`** layout:
   - Module docstring: purpose, idempotency, Susan backup guidance, recommended operator order (see Stage 2).
   - `sys.path.insert(0, str(Path(__file__).parent.parent.parent))`.
   - **`argparse`** flags:
     - `--dry-run` — preview only; no `DELETE`.
     - `--skip-board-cleanup` — run identity dedupe only.
     - `--skip-dedupe` — run board-gaze cleanup only.
     - `--company SHORT_NAME` — when set, restrict identity dedupe to groups where `company = ?` (board cleanup still runs unless `--skip-board-cleanup`).

2. **Imports:**
   - `_get_connection`, `_ensure_job_schema`, `_run_with_retry` from **`src.data.database`**
   - `BOARDS_CONFIG` from **`src.utils.config`**
   - `sqlite3`, `argparse`, `sys`, `Path`, `typing` as needed.

3. **Board-gaze prefix constant** (do not hardcode inline):
   ```python
   _BOARD_PREFIX = BOARDS_CONFIG["ingest"]["placeholder_company_prefix"]  # "__board__"
   _BOARD_LIKE = f"{_BOARD_PREFIX}%"
   ```

4. **Summary count keys** (single dict reused across phases):
   `board_jobs_scanned`, `board_jobs_deleted`, `dedupe_groups`, `dedupe_survivors`, `dedupe_deleted`, `errors`.

5. **`find_duplicate_identity_groups(conn, company_filter: Optional[str]) -> List[dict]`** — read-only query inside `_run_with_retry`:
   - Select groups where **all three** identity columns are populated (non-NULL **and** non-empty string after strip): `company`, `job_title`, `company_job_id`.
   - Exclude board placeholder companies: `company NOT LIKE ?` with `_BOARD_LIKE`.
   - Optional `--company` filter: `AND company = ?`.
   - SQL shape (implement literally; adjust only if SQLite syntax requires):
     ```sql
     SELECT company, job_title, company_job_id, COUNT(*) AS cnt
     FROM job
     WHERE company IS NOT NULL AND TRIM(company) != ''
       AND job_title IS NOT NULL AND TRIM(job_title) != ''
       AND company_job_id IS NOT NULL AND TRIM(company_job_id) != ''
       AND company NOT LIKE ?
       /* optional: AND company = ? */
     GROUP BY company, job_title, company_job_id
     HAVING COUNT(*) > 1
     ```
   - For each group row, fetch member jobs ordered by **`created_at ASC NULLS LAST`**, then **`astral_job_id ASC`** as tie-breaker:
     ```sql
     SELECT astral_job_id, created_at, state
     FROM job
     WHERE company = ? AND job_title = ? AND company_job_id = ?
     ORDER BY created_at ASC NULLS LAST, astral_job_id ASC
     ```
   - Return list of dicts: `{company, job_title, company_job_id, members: [{astral_job_id, created_at, state}, ...]}`.

   ⚠️ **Decision:** Survivor = **first row** in that ordered list (minimum `created_at`; deterministic tie on `astral_job_id`). Matches parent AC “minimum `created_at` within each group.”

   ⚠️ **Decision:** NULL **or** blank identity columns are **out of scope** — they never enter a dedupe group (pre-Consult rows stay untouched).

6. **`delete_jobs_by_astral_job_ids(conn, ids: List[str]) -> int`** — script-local helper (not `database.py` public API):
   - No-op when `ids` empty.
   - `DELETE FROM job WHERE astral_job_id IN (...)` with parameterized placeholders.
   - `conn.commit()`; return `cursor.rowcount`.
   - **Do not** DELETE/UPDATE `agent_data`, timesheets, `dispatch_ledger`, or any other table.

7. **`run_identity_dedupe(dry_run, company_filter, counts) -> None`:**
   - Call `_ensure_job_schema(conn)` before queries.
   - For each duplicate group from step 5:
     - `survivor = members[0]`; `to_delete = members[1:]`.
     - Increment `counts["dedupe_groups"]`; increment `counts["dedupe_survivors"]` once per group.
     - If **`--dry-run`**: print one line per deleted id:
       `[dedupe] DRY RUN — group ({company}, {job_title}, {company_job_id}): keep {survivor_id} (created_at={survivor_ts}); would delete {n} rows: {id_list}`
     - Else: call `delete_jobs_by_astral_job_ids` for delete ids; add rowcount to `counts["dedupe_deleted"]`; print same line without `DRY RUN`.
   - Wrap each group in try/except; on exception print `[dedupe] error …` and increment `counts["errors"]` (continue other groups).

8. **`run_board_gaze_cleanup(dry_run, counts) -> None`:**
   - Before delete, count rows: `SELECT COUNT(*) FROM job WHERE company LIKE ?` with `_BOARD_LIKE`; store in `counts["board_jobs_scanned"]`.
   - If count is 0: print `[board] no placeholder-company jobs found`; return.
   - If **`--dry-run`**: print `[board] DRY RUN — would delete {n} job rows where company LIKE '{_BOARD_LIKE}'`; set `counts["board_jobs_deleted"] = n` for summary (would-delete count).
   - Else: `DELETE FROM job WHERE company LIKE ?`; set `counts["board_jobs_deleted"] = cursor.rowcount`; print `[board] deleted {n} job rows`.

   ⚠️ **Decision:** Board cleanup is a **bulk delete by company prefix**, not per-company iteration — placeholder companies are decommissioned entirely; no dedupe among board rows.

9. **`run_cleanup(dry_run, skip_dedupe, skip_board, company_filter) -> None`:**
   - Print `=== DRY RUN — no DB writes ===` banner when `dry_run`.
   - **Order:** board-gaze cleanup first (unless `--skip-board-cleanup`), then identity dedupe (unless `--skip-dedupe`).
   - Print final summary block:
     ```
     === SUMMARY ===
     board: scanned={board_jobs_scanned} deleted={board_jobs_deleted}
     dedupe: groups={dedupe_groups} survivors_kept={dedupe_survivors} rows_deleted={dedupe_deleted}
     errors={errors}
     ```

10. **`if __name__ == "__main__"`** — parse args, call `run_cleanup`, exit non-zero if `counts["errors"] > 0` after live run.

---

## Stage 2: Operator runbook (in script docstring)

**Done when:** Susan can run safely on staging/local/Railway snapshot without reading source.

1. In module docstring, document **recommended order**:
   ```bash
   # 1. Backup: cp data/astral.db data/astral.db.pre-AST-729-$(date +%Y%m%d)
   # 2. Dry-run full cleanup (both phases)
   python scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py --dry-run
   # 3. Spot-check one company’s dedupe groups
   python scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py --dry-run --company aledade
   # 4. Optional: board phase only preview
   python scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py --dry-run --skip-dedupe
   # 5. Live run (after Susan OK)
   python scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py
   # 6. Verify agent_data untouched (optional):
   #    SELECT COUNT(*) FROM agent_data;  — same before/after
   ```

2. Note: **Idempotent** — second live run should report `dedupe_groups=0` (no duplicate triples left) and `board_jobs_scanned=0` after board rows are gone.

3. Note: **Run before AST-732** unique index migration in each environment so index creation does not fail on existing duplicates.

---

## Stage 3: Compile gate

**Done when:** `python -m py_compile scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py` passes.

1. Run compile on the new script before **Code Complete**.

---

## Execution contract

Binding per **plan-child**: stages **1 → 2 → 3** in order; **one commit per stage** on epic worktree during **build-child**, publish each to **`origin/sub/AST-728/AST-729-duplicate-board-gaze-cleanup-migration`**. Do not edit **`tests/`** or **`docs/test-bible/**`**. On ambiguity — **`🛑 Stage N blocked`** on **AST-728** parent; stop.

---

## Self-Assessment

**Scope:** `Single-Component` — one migration script under `scripts/migrations/`; no runtime Tracker/Gazer/Consult changes and no new database public APIs.

**Conf:** `high` — duplicate survivor rule and board prefix are fully specified in the ticket and parent epic; migration layout mirrors existing backfill scripts and `_remove_jobs_by_company` DELETE precedent.

**Risk:** `Medium` — deleting the wrong job row removes pipeline history for that `astral_job_id` (related audit rows remain orphaned); mitigated by `--dry-run`, deterministic survivor ordering, and explicit exclusion of incomplete identity triples.

---

## Self-review against ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.3 DRY | One script with shared delete helper; reuses `_run_with_retry` / `_ensure_job_schema` instead of new database surface. |
| §2.1 config | Board prefix from `BOARDS_CONFIG["ingest"]["placeholder_company_prefix"]`; no new config keys. |
| §2.4 batch | Offline migration only; no batch claim/clear changes. |
| §2.6 state machine | Script does not transition job states — hard DELETE only. |
| §3.3 imports | Script imports `database` + `config` only (same as other migrations). |
| §3.6 spikes | Any investigation under `debug/spikes/AST-729/` only. |

No unresolved conflicts.

---

## Review

**Branch:** `origin/sub/AST-728/AST-729-duplicate-board-gaze-cleanup-migration`  
**Diff baseline:** `origin/dev`  
**Review tip:** `c6fa284`

**Built:** Stages 1–3 — `cleanup_duplicate_and_board_gaze_jobs.py` with board-gaze bulk delete (`__board__*` prefix from config), identity dedupe (earliest `created_at` survivor, `astral_job_id` tie-break), `--dry-run` / phase skip / `--company` filters, operator runbook in module docstring; Betty manifest + component tests on `origin/tests` merge.

### What's solid

- Plan fidelity: board prefix from `BOARDS_CONFIG`, parameterized SQL, survivor ordering (`created_at ASC NULLS LAST`, `astral_job_id ASC`), board phase before dedupe, all CLI flags, operator runbook in module docstring.
- Scope clean: single migration script under `scripts/migrations/`; no `src/` product changes; no AST-732/733 scope smuggled.
- Resilience: `_run_with_retry` on DB paths; per-group try/except prints `[dedupe] error …`, increments `counts["errors"]`, live run exits non-zero when errors > 0.
- Tests: component suite matches test-bible manifest — discovery/exclusions, delete helper, board dry-run/live/empty, dedupe dry-run/live/error path, phase order and skip flags.

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| — | — | No fix-now items. |

### Recommended actions

| Severity | Location | Action |
| --- | --- | --- |
| advisory | `tests/component/scripts/test_cleanup_duplicate_and_board_gaze_jobs.py` | Optional: import board prefix from `BOARDS_CONFIG` instead of hardcoding `"__board__"` so tests track config drift. |
| advisory | same | Optional: assert `agent_data` (or related-table) row counts unchanged after live delete — operator runbook step 6 already covers manual verify. |

---

## Resolution

**Date:** 2026-06-18  
**Resolved by:** Hedy (resolve-child)

Radia posted **no fix-now** items. Advisory notes (hardcoded `"__board__"` in tests; optional related-table count assertion) accepted as documented — Betty owns test-tree; operator runbook covers manual `agent_data` verify.

**§9a dry-run:** `origin/sub/AST-728/AST-729-duplicate-board-gaze-cleanup-migration` @ `28ae93a` merges cleanly into **`origin/dev`** and **`origin/ftr/duplicate-jobs-ingested`**.

**Product changes in resolve:** none — review clean. Manifest re-run: 12 passed.

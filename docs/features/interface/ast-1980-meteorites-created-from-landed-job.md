# AST-1980 — Meteorites Created from landed job

- **Linear:** [AST-1980](https://linear.app/astralcareermatch/issue/AST-1980) · parent [AST-1971](https://linear.app/astralcareermatch/issue/AST-1971) (Add Created to the job list table)
- **Publish ref:** `origin/sub/AST-1971/AST-1980-created-col`
- **Canon Scope (this child):** `stat.logging.error`, `stat.logging.info.api`.

Jobs → Meteorites gains a sortable **Created** column showing the **landed job's** `created_at` (not the meteorite row's own), placed immediately left of **State Changed**. The value comes from the `LEFT JOIN job` that `list_meteorites_for_candidate` already runs for `job_state` (AST-1976) — one more aliased column on the same `SELECT`, no second query. `api_meteorite._LIST_KEYS` carries the new key through the list projection, and `JOBS_METEORITES_LIST_COLUMNS` serves the column to `JobsMeteorites.tsx` through `ListPage`, which already formats `type: "datetime"` cells (`—` for null) and sorts any sortable column. No React file and no job list page is touched — those are sibling [AST-1979](https://linear.app/astralcareermatch/issue/AST-1979).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | `list_meteorites_for_candidate`: add `j.created_at AS job_created_at` to the existing `SELECT`; docstring mentions it | data |
| `src/ui/api/api_meteorite.py` | `_LIST_KEYS`: add `"job_created_at"` after `"job_state"` | ui (api) |
| `src/utils/config.py` | `JOBS_METEORITES_LIST_COLUMNS`: insert the Created entry immediately before the `state_changed_at` entry | utils |

No other file. In particular **not** edited: anything under `src/ui/frontend/` (including `JobsMeteorites.tsx`, `ListPage.tsx`, `lib/fmt.ts`), `_DETAIL_KEYS`, `get_meteorite`, `_meteorite_row_to_dict`, the job list pages, `UI_CONFIG`. No `tests/` or bible edits (Betty owns them).

⚠️ **Decision — key name `job_created_at`.** Mirrors the AST-1976 `job_state` alias (landed-job field, `job_` prefix). It is distinct from the meteorite's own `created_at`, which `m.*` still supplies untouched (AC 6). `rg -n job_created_at src/` returns nothing on the branch point, so it collides with nothing.

⚠️ **Decision — null handling is inherited, no new code.** `LEFT JOIN` yields `NULL` when `astral_job_id` is null or no job matches. `_row_to_dict` passes it through as `None` and `_project_meteorite` emits it as JSON `null`. In `ListPage`, the column has no `render` override (`JobsMeteorites.tsx` only overrides `astral_job_id` and `job_state`), so the cell goes through `formatCell(raw, "datetime")`. That function returns `—` for null and `fmtTime(...)` otherwise, which is the same path `state_changed_at` takes today. Sort uses `ListPage.cmpValues` (null → `""`), the same as State Changed.

⚠️ **Decision — no `defaultDesc` on the Created entry.** AC 7 requires only `type: "datetime"` and `sortable: true`. Without `defaultDesc`, the first click sorts ascending and the second reverses, which matches the first-click rule sibling AST-1979 uses for Created on the job pages. **Default-sort impact:** `ListPage`'s default sort is every sortable column in order, so `job_created_at` becomes a tie-breaker between `job_state` and `state_changed_at`. It cannot change the default order. Rows tie on all earlier keys (including `astral_job_id`) only if they are both unlanded, where both `job_created_at` values are null and the tie-break falls through to `state_changed_at`, or if they share the same landed job, where both `job_created_at` values are equal and it also falls through.

⚠️ **Decision — logging.** `meteorite_list_for_candidate` is unchanged. Its existing single `logger.exception` handler (live facts, next step, no re-raise) already wraps the extended read (`stat.logging.error`). It is a state-returning GET, so no info line (`stat.logging.info.api`). `src/data/` does not log. No `logger.*` line is added anywhere (AC 9).

## Stage 1: Landed-job `created_at` on the Meteorites list API + Created column config

**Done when:** `GET /api/candidates/<id>/meteorites` returns `job_created_at` on every row (the landed job's `job.created_at`, `null` when unlanded) with `created_at` still the meteorite's own, and `columns` contains `{"key": "job_created_at", "label": "Created", "sortable": True, "type": "datetime"}` immediately before the `state_changed_at` entry. `python -c "import src.utils.config"` exits 0.

### `src/data/database.py`

1. In `list_meteorites_for_candidate` (currently ~line 4179), change the `SELECT` line from
   ```
   """SELECT m.*, j.state AS job_state FROM meteorite m
   ```
   to
   ```
   """SELECT m.*, j.state AS job_state, j.created_at AS job_created_at FROM meteorite m
   ```
   Leave the `LEFT JOIN job j ON j.astral_job_id = m.astral_job_id`, `WHERE`, `ORDER BY`, params, and `_meteorite_row_to_dict` mapping exactly as they are. Do not add a second query or any per-row `get_job` call (AC 8).
2. Update the existing comment above the query from `# LEFT JOIN keeps unlanded rows; alias avoids shadowing meteorite.state.` to `# LEFT JOIN keeps unlanded rows; aliases avoid shadowing meteorite.state / meteorite.created_at.`
3. Update the docstring to: `"""Return all meteorite rows for candidate_id, newest state_changed_at first; job_state / job_created_at = landed job's current state / created_at (None when unlanded)."""`

### `src/ui/api/api_meteorite.py`

4. In `_LIST_KEYS`, change the line
   ```
   "classify_outcome", "link", "astral_job_id", "job_state",
   ```
   to
   ```
   "classify_outcome", "link", "astral_job_id", "job_state", "job_created_at",
   ```
   No other edit in this file: no change to `_DETAIL_KEYS`, `_project_meteorite`, or `meteorite_list_for_candidate`, and no new `logger` call.

### `src/utils/config.py`

5. In `JOBS_METEORITES_LIST_COLUMNS` (currently ~line 3496), insert this entry between `{"key": "job_state", "label": "Job State", "sortable": True},` and the `state_changed_at` dict:
   ```python
   {"key": "job_created_at", "label": "Created", "sortable": True, "type": "datetime"},
   ```
   Leave every other entry, including `state_changed_at`'s `defaultDesc: True`, unchanged.

### Verify (before commit)

6. `python -c "import src.utils.config"` exits 0 (AC 10).
7. `python -m py_compile src/data/database.py src/ui/api/api_meteorite.py src/utils/config.py` exits 0.
8. Lint gate: the repo has no Python linter config (`pyproject.toml` / `setup.cfg` / `.flake8` / `ruff.toml` absent; `ruff` / `flake8` not installed at plan time), so steps 6–7 are the Python compile/lint gate. Do not install or configure a linter. No frontend file changes, so `npm run lint` / `npm run build` are not part of this ticket.
9. `git diff origin/dev -- src/ui/api/api_meteorite.py | rg "^\+.*logger\.(info|exception|warning|error)"` returns nothing (AC 9).
10. `git diff origin/dev --stat -- src/ui/frontend/` is empty (AC 7, Boundaries).
11. Run the existing component tests that touch these symbols and confirm they are green or failing only because of the intended new key/column: `pytest tests/component/data/database/test_meteorites.py tests/component/ui/api/test_api_meteorite.py tests/component/utils/test_config.py -q`. If a test pins the exact `_LIST_KEYS` / column list and fails only for that reason, do **not** edit it. Note it in the stage comment for Betty (qa-child).
12. Commit: `code(AST-1980): Meteorites Created — landed job created_at on list API + config column`. Publish per build-child (`git push origin HEAD:sub/AST-1971/AST-1980-created-col`).

## AC map

- AC 6: steps 1, 4. `job_created_at` comes from `job.created_at` via the join. `m.*` keeps the meteorite's own `created_at`. The page shows `—` for null (inherited `formatCell`).
- AC 7: step 5 adds the column. The page sorts it via `ListPage.handleSort` with no page code, and step 10 checks the diff.
- AC 8: step 1 (same `SELECT`, one join).
- AC 9: Decision on logging and step 9.
- AC 10: step 6.

## Tests affected (for Betty, informational)

Existing files referencing these symbols: `tests/component/ui/api/test_api_meteorite.py`, `tests/component/data/database/test_meteorites.py`, `tests/component/utils/test_config.py`, `tests/component/ui/api/test_api_system.py`, `tests/component/data/database/test_jobs.py`, `tests/component/frontend/pages/test_JobsMeteorites.test.tsx`. Any test asserting the exact `_LIST_KEYS` tuple or the exact `JOBS_METEORITES_LIST_COLUMNS` list/length will need the new entry.

## Estimate

Confirm Chuckles estimate: 2 — agree

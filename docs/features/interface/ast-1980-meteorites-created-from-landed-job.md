<!-- linear-archive: AST-1980 archived 2026-10-08 -->

## Linear archive (AST-1980)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1980/meteorites-created-from-landed-job-add-created-to-the-job-list-table  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1971 — Add Created to the job list table  
**Blocked by / blocks / related:** parent: AST-1971

### Description

## What this implements

Delivers the landed job's `created_at` on the Meteorites list API, plus a config-driven, sortable Created column on Jobs → Meteorites. Does not touch any React file or the job list pages (#1).

## Citations

`stat.logging.error` (the existing list handler wraps the extended read; no new handler); `stat.logging.info.api` (GET route, no info line added).

## Scope

`src/data/database.py` (`list_meteorites_for_candidate` also returns the landed job's `created_at` under a distinct key, from the same lookup AST-1970 adds); `src/ui/api/api_meteorite.py` (`_LIST_KEYS` includes that key); `src/utils/config.py` (`JOBS_METEORITES_LIST_COLUMNS` gains a sortable `datetime` Created entry before `state_changed_at`).

## Acceptance criteria

 6. **Meteorites Created = landed job's** `created_at`**.** For every row in `GET /api/candidates/X/meteorites` with a non-null `astral_job_id`, the landed-job created value equals `SELECT created_at FROM job WHERE astral_job_id = <that id>`. Rows with no `astral_job_id` carry null, and the page shows `—`. The row's own `created_at` still equals `meteorite.created_at`. **Fail:** the meteorite's timestamp shown as Created, a mismatch with the job row, or the meteorite's own `created_at` overwritten.
 7. **Meteorites column via config, not page code.** The response's `columns` contains a `Created` entry with `type: "datetime"` and `sortable: true`, placed immediately before `state_changed_at`. On the page, clicking `Created` sorts the rows by that value. `git diff origin/dev -- src/ui/frontend/src/pages/JobsMeteorites.tsx` is empty. **Fail:** column missing / misplaced, unsortable, or a hardcoded column added in the page.
 8. **One landed-job lookup.** `list_meteorites_for_candidate` gets the landed job's state (AST-1970) and `created_at` from the same lookup: one join / query, not a second per-row fetch. **Fail:** a separate query or per-row `get_job` call added for `created_at`.
 9. **No new logging on the list route.** `git diff origin/dev -- src/ui/api/api_meteorite.py | rg "^\+.*logger\.(info|exception|warning|error)"` returns nothing. **Fail:** any hit.
10. **Builds clean (backend half).** `python -c "import src.utils.config"` exits 0. **Fail:** non-zero exit.

## Boundaries

Does **not** touch any file under `src/ui/frontend/` (including `JobsMeteorites.tsx`, which renders config-served columns through `ListPage`), and does not touch the job list pages. Those belong to sibling #1 (Created column on Jobs list tables).

## Notes for planning

On `dev`, `list_meteorites_for_candidate` already does `SELECT m.*, j.state AS job_state FROM meteorite m LEFT JOIN job j ON j.astral_job_id = m.astral_job_id` (from AST-1970). Extend that select by one aliased column, under a key that is **distinct** from the meteorite's own `created_at`. The key name is plan-child's call. Citations: `stat.logging.error`, `stat.logging.info.api`.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1971-created-col`, child `sub/AST-1971/AST-1980-created-col`. Created at dispatch-parent. Resolve with `epic_registry.py show AST-1971`.

### Comments

#### radia — 2026-10-04T21:17:46.956Z
[code-rubric] PROCEED (Commit: 02fc15a18) Join+config Created column

#### betty — 2026-10-04T21:15:45.989Z
`origin/sub/AST-1971/AST-1980-created-col` @ `02fc15a18` · Meteorites Created tests ready

#### joan — 2026-10-04T21:09:44.616Z
[plan-rubric] PROCEED (Commit: 6cb5423c8) Join + config Created

#### hedy — 2026-10-04T21:08:52.016Z
`origin/sub/AST-1971/AST-1980-created-col` @ `6cb5423c8` · one join, config column

---

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


## Review

- **Branch:** `origin/sub/AST-1971/AST-1980-created-col`
- **Build commits:** `7beb35926` (Stage 1: `job_created_at` on the list join + `_LIST_KEYS` + Created config column)
- **Build notes:** `python -c "import src.utils.config"` and `py_compile` on all three files exit 0. AC 9 `rg` on the `api_meteorite.py` diff returns nothing. `git diff origin/dev -- src/ui/frontend/src/pages/JobsMeteorites.tsx` is empty. This ticket's own diff touches no frontend file; the `src/ui/frontend/` lines in `git diff origin/dev` are sibling AST-1979, carried in from `origin/ftr/AST-1971-created-col`. No Python linter is configured (plan step 8).
- **Deviation:** none.
- **For QA:** existing failures are the same with and without this change: `test_config.py` has 21 identical failures before and after. `test_meteorites.py` fails to collect (`ImportError: METEORITE_STATES_RETENTION` is not in `config.py`). `test_api_meteorite.py` fails to collect (`ModuleNotFoundError: asyncpg` in this env). None of them assert the new key/column yet. No manual browser smoke run in this headless build.

## Joan validate

```text
[plan-rubric]
**Ticket:** AST-1980
**Overall:** APPROVED
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Publish ref:** 6cb5423c8511b461b43a14cc2fe9ddc7e8284658

## Canon scores
stat.logging.error | A |
stat.logging.info.api | A |

## Traceability
AC 6 → steps 1, 4; AC 7 → steps 5, 10; AC 8 → step 1; AC 9 → logging decision + step 9; AC 10 → step 6; parent AC 1–5 N/A (sibling AST-1979 job list pages).

### Findings

**discuss** · Workflow · Assignee was Hedy, not Joan, at `get-issue` — Chuckles should assign Joan before validate-plan handoff per skill §1; review proceeded on request.

**acceptable** · Plan intro · References AST-1976 for the existing `job_state` join while ticket notes cite AST-1970 — same landed-job join; fix typo in plan prose only if you want consistency.

**acceptable** · Plan · `defaultDesc` omission + ListPage multi-column default sort tie-break (new `job_created_at` between `job_state` and `state_changed_at`) is argued in the Decision block; plausible and bounded to ties — monitor in UAT if sort feel matters.

**acceptable** · Stage 1 step 11 · Directs engineer not to patch component tests and to hand list-key failures to Betty — matches qa-child ownership.

**discuss** · Canon Scope gap (not scored) · `astral.config.config-source-of-truth` plainly governs `JOBS_METEORITES_LIST_COLUMNS`; plan correctly uses config, but id is not on the frozen two-statute list — optional parent Canon Scope amend only if Archie wants config cited on every config.py touch.

context_tokens≈36000
```


## Radia review

[code-rubric]
**Ticket:** AST-1980
**Publish ref:** `02fc15a18bdd3f38482e8e0b9cd051cf91701304` (`origin/sub/AST-1971/AST-1980-created-col`)
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** CLEAN

## Canon scores

stat.logging.error | A |
stat.logging.info.api | A |

## Column diff vs plan stage

(aligned) — Joan scored both statutes **A**; code review matches (handler unchanged; data layer still raises/logs-not; no new `logger.*` on the list route diff).

## Frame diff

(none)

### Findings

**advisory** · Three-dot diff · **Sibling product carry (not AST-1980 scope):** `src/ui/frontend/src/pages/Jobs{Recommended,Processing,Skipped,Applied}.tsx` and AST-1979 test/bible paths appear on the branch tip from epic/ftr/merge-tests. **AST-1980 product scope** is only `database.py`, `api_meteorite.py`, `config.py`; `git diff origin/dev...origin/sub/AST-1971/AST-1980-created-col -- src/ui/frontend/src/pages/JobsMeteorites.tsx` is **empty** (AC 7).

**advisory** · `tests/**` + `docs/test-bible/**` · **Sibling test carry:** AST-1979 (`created-column.ts`, four Jobs page suites, `pages.md` § AST-1979) and AST-1978 (`test_api_admin.py`, `test_AdminTaskPrompts`, `api_admin.md`) ride merge-tests; Betty’s AST-1980 block lives in `api_meteorite.md` + `TestAst1980MeteoriteJobCreatedAt`, `test_list_projects_landed_job_created_at_ast1980`, config case, `test_JobsMeteorites` § AST-1980.

**advisory** · Canon Scope · Joan noted optional future cite of `astral.config.config-source-of-truth` for `JOBS_METEORITES_LIST_COLUMNS` touches; frozen list is logging-only by design — not an ESCALATE (Discussion locked two statutes; implementation follows config column pattern correctly).

### What's solid

- **AC 6 / 8:** Single `SELECT` adds `j.created_at AS job_created_at` on the existing `LEFT JOIN`; `m.*` preserves meteorite `created_at`; `_LIST_KEYS` exposes `job_created_at` after `job_state`.
- **AC 7:** Config inserts sortable datetime **Created** immediately before **State Changed**; page unchanged — `ListPage` formats/sorts via `type: "datetime"`.
- **AC 9:** `api_meteorite.py` diff is `_LIST_KEYS` only; `rg` on added lines finds no new `logger.(info|exception|warning|error)`; existing `logger.exception` on list failure still wraps the read.
- **AC 10:** Config import path is a one-line column dict — consistent with plan.
- **Tests:** DB case proves landed vs unlanded/orphan `job_created_at`, distinct `created_at`, and one SELECT with trace + `get_job` fail guard; API case projects both timestamps and asserts no log calls on success; Vitest proves Created left of State Changed, `fmtTime(job_created_at)`, `—` unlanded, sort toggle without page edits.
- **Plan fidelity / estimate 2:** Matches Stage 1 steps; no boundary violations on frontend page source.

### Recommended actions (downstream — not for Radia)

- Chuckles: append artifact, `docs(AST-1980): Radia review — clean`, push publish ref, post slim upshot `--as radia`, **Review Posted** → **PROCEED** (no `resolve-child` unless datt says otherwise).
- UAT (optional): Joan’s plan note — `defaultDesc`-less Created only affects multi-key tie-break order on Meteorites; watch sort feel if Susan cares.

context_tokens≈42000

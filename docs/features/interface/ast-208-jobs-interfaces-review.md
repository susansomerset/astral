# AST-208: Jobs Interfaces — Code Review

**Branch:** `<agent>/ast-208-jobs-interfaces`
**Commit:** `1bff91f`
**Reviewer:** Chuckles

---

## Overall Assessment

**Ship it.** Clean execution of the Companies pattern. The route-ordering lesson from AST-207 was learned and applied — `bulk_state` is explicitly registered before `/<astral_job_id>` with a comment. The `_SKIPPED_STATES` duplication between `jobs.py` and `system.py` is the only thing worth cleaning up. Everything else is solid.

---

## `src/data/database.py` — `list_jobs` / `count_jobs`

**`order_by` injection guard is correct:**

```python
_SORTABLE = {"state_changed_at", "created_at", "updated_at", "job_title", "company", "state"}
col = order_by if order_by in _SORTABLE else "rowid"
```

`_SORTABLE` is defined inside `list_jobs` but outside `_with_conn`. That's fine — it's a module-level constant that happens to be scoped to the function. Could be a module-level constant (e.g., `_LIST_JOBS_SORTABLE`) to make it more visible, but no real issue.

**`NULLS LAST` in SQLite:**

```python
f"SELECT * FROM job{where} ORDER BY {col} DESC NULLS LAST"
```

`NULLS LAST` is supported in SQLite 3.30.0+ (2019). Railway's production Python image almost certainly ships a modern enough SQLite, but worth a note — older SQLite would silently error on this syntax. Low risk.

**`count_jobs` avoids full row fetch** — correct, uses `SELECT COUNT(*)`. This is the fix that was recommended for the companies API and it's applied correctly from the start here.

**`candidate_id` scopes via subquery on `company`** — consistent with `claim_job_batch`. Correct.

---

## `src/ui/api/jobs.py`

### Route ordering — explicitly handled

```python
# Named GET routes registered before /<astral_job_id> to avoid Flask swallowing them
@jobs_bp.route("/bulk_state", methods=["POST"])
```

The comment is there, the ordering is correct. Good — the ast-207 bug was caught and the fix was internalized, not just applied.

### `bulk_state` uses `save_job` instead of `update_company`-style update

```python
for job_id in ids:
    save_job(job_id, state=to_state)
    updated += 1
```

`updated` is always `len(ids)` — it increments unconditionally regardless of whether `save_job` actually found and updated the row. If a job_id in the list doesn't exist, `save_job` would insert a new minimal row (upsert semantics) rather than silently skip. Depending on `save_job`'s implementation, this could create ghost job records. Worth verifying that `save_job` won't insert a bare row with only `astral_job_id` and `state` set.

### `_SKIPPED_STATES` is defined twice

In `jobs.py`:
```python
_SKIPPED_STATES = list(_FAILED_STAGE_LABEL.keys())
```

In `system.py`:
```python
_SKIPPED_STATES = ["FAILED_JOBLIST", "FAILED_JD", "FAILED_GET", "FAILED_DO", "FAILED_LIKE"]
```

These happen to be the same list today, but they're in sync by coincidence. If a new `FAILED_*` state is added, the developer needs to update both. The `system.py` copy should import from `jobs.py` (or both should import from a shared constant in `config.py`). Low priority but it's a real maintenance trap.

### `_flatten_skipped` first-F-grade extraction is clean

```python
for g in grades:
    if g.get("grade") in ("F", "X") and g.get("reason"):
        job["fail_reason_summary"] = g["reason"]
        break
```

Surfaces the first failing grade reason. Handles missing `grade` and `reason` keys defensively. The "X" grade inclusion alongside "F" is intentional — worth a comment noting what "X" represents (presumably an error/exception grade vs a normal fail).

---

## `src/ui/api/system.py`

**`_get_job_counts` mirrors `_get_company_counts` exactly** — same try/except pattern, same empty-dict-on-error behavior, same `candidate_id` guard. Consistent.

**`nav_counts = {**company_counts, **job_counts}`** — clean merge. If a path ever appeared in both, `job_counts` would win. No path overlap currently.

---

## `src/utils/config.py`

**`DATA_SHAPES["jobs"]`** — column definitions are correct. `defaultDesc: True` on the timestamp columns means the default sort is newest-first for all three views. Good UX default.

**`"Meteors"` is now `enabled: False`** in NAV_CONFIG. This preserves the label in the nav (for familiarity) while routing disabled. The `/jobs/meteors` route still works in `routes.tsx` as an alias to `Recommended`. Clean transition.

---

## Frontend pages

### `Recommended.tsx`

**`fmtScore` handles null/undefined correctly:**
```tsx
function fmtScore(v: number | null | undefined): string {
  if (v == null) return "—"
  return `${(v * 100).toFixed(0)}%`
}
```

`== null` catches both `null` and `undefined`. Correct. The `toFixed(0)` truncates — so 0.999 displays as "100%" and 0.001 displays as "0%". Acceptable for display.

**`jd?.job_description` rendered in a `<pre>` tag** — preserves whitespace/newlines from the scraped job description. Good call.

**`const jd = viewing?.job_data as Record<string, unknown> | undefined`** — declared at component scope, not inside the modal. This means `jd` is re-evaluated on every render even when the modal is closed (`viewing` is null). Harmless since it's just a variable assignment, not a computation.

### `New.tsx`

No Toast. `New` has no bulk actions, so no toast needed — correct. The modal shows link only if `job_link` is non-null. Clean.

### `Skipped.tsx`

**`clearToast` is correctly hoisted:**
```tsx
const clearToast = useCallback(() => setToast(null), [])
```
No inline-JSX hook violation (the ast-207 bug). Good.

**`gradeKey` map is defined inside the component body** but outside the render return — recreated on every render as a plain object literal. Fine, but could be a module-level constant since it never changes.

**IIFE for grades rendering inside JSX:**
```tsx
{(() => {
  const key = gradeKey[viewing.state]
  ...
})()}
```

This pattern works but is less readable than extracting to a named helper or a small subcomponent. For a modal that's unlikely to grow much, it's acceptable.

**Grade display: `g.grade` + `g.reason`** — renders all grades for the failed stage, not just the failing ones. A job that failed GET but had some passing vectors will show all of them. This is probably the right call for a diagnostic modal — seeing the full picture is useful.

### `Applied.tsx` / `Responded.tsx` — correct stubs

Empty `ListPage` with no loading/data state. Shows the page title and an empty table. Better than the previous `StubPage` because it uses the actual layout component. If a user lands on either page before they're implemented, they see a real (empty) list rather than a "coming soon" placeholder.

---

## `routes.tsx`

**`/jobs/meteors` and `/jobs/recommended` both render `<Recommended />`** — backward-compatible alias. The nav badge route is `/jobs/recommended`. The Meteors nav item is `enabled: false` so it won't appear to live users. Anyone who bookmarked `/jobs/meteors` still lands on the right page.

**Default redirect updated** from `/jobs/meteors` to `/jobs/recommended`. Catch-all updated too. Both correct.

---

## Summary of actionable items

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | Medium | `jobs.py` `bulk_state` | `save_job` is upsert — passing a nonexistent `astral_job_id` may create a ghost row. Verify `save_job` won't INSERT on unknown IDs, or swap for a dedicated update function |
| 2 | Low | `jobs.py` + `system.py` | `_SKIPPED_STATES` defined in both files — single source of truth needed |
| 3 | Note | `jobs.py` `_flatten_skipped` | Grade value `"X"` checked alongside `"F"` — a comment explaining what X represents would help future readers |
| 4 | Note | `Skipped.tsx` | `gradeKey` map could be a module-level constant instead of recreated per render |
| 5 | Note | `database.py` | `NULLS LAST` requires SQLite 3.30.0+ — low risk on Railway but worth a note |

Item 1 is the only one with real correctness risk. Items 2–5 are polish.

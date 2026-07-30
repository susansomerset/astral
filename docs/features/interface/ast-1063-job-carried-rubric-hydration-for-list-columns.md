# Job-carried rubric hydration for list columns

**Linear:** [AST-1063](https://linear.app/astralcareermatch/issue/AST-1063/job-carried-rubric-hydration-for-list-columns-issue-with-the-rubric)  
**Parent:** [AST-1059 — Issue with the rubric grade displays on the Jobs List pages](https://linear.app/astralcareermatch/issue/AST-1059/issue-with-the-rubric-grade-displays-on-the-jobs-list-pages)  
**Publish ref (origin):** `sub/AST-1059/AST-1063-job-carried-rubric-hydration-for-list-columns`  
**Parent integration ref:** `ftr/AST-1059-rubric-grade-displays-jobs-list`  
**Blocks:** [AST-1064](https://linear.app/astralcareermatch/issue/AST-1064/group-by-aligned-rubric-jobs-list-tables-issue-with-the-rubric-grade) (consumer of this payload; list grouping / grade-dot / Score paint)

Persist and surface the **analysis-time rubric criteria** with each graded job so Skipped / In Review list APIs return a job-carried hydrated rubric for headers and tooltips — never forcing list consumers to read the **live** candidate rubric artifact. Also keep analysis-time scores visible on the same list payload (already partially lifted). Does **not** own Jobs list grouping UI, grade-dot paint, Score column rendering, Recommended phase-score layout, re-grading, or live rubric edits.

---

## Discovery (binding)

Parent wording said the fully hydrated rubric “already lives with the job’s analysis data.” **That is false today.**

- Grade write paths (`_apply_render_verdict_decoded_job`, qualify `joblist_*`, evaluate `jd_*`) call `_rubric_criteria_for_cfg` / `rubric_list` only to hydrate reasons and score, then save `{prefix}_grades` (+ optional `{prefix}_score` / notes). **No rubric criteria list is written to `job_data`.**
- List UI (`JobsSkipped.tsx` / `JobsInReview.tsx`) builds columns via `buildJobListRubricColumns` from **live** `candidate_data.artifacts[JOBS_UI_GRADE_RUBRIC[gradeKey]]` — the UAT dash sea when live rubric labels diverge from stored grade `vector` names.
- Grades already carry analysis-time **vector labels**, letters, confidence, and often **reason** text. Missing for headers: **code**, **importance**, **grade_descriptions** (for tip fallback when reason empty).

This ticket **must** snapshot criteria at write time, then lift them on list responses. Historical jobs without a snapshot stay without `{prefix}_rubric` until re-graded; AST-1064 defines any grades-only fallback for those rows.

---

## Prerequisite gate (before Stage 1 of build-child)

1. On epic worktree: `git fetch origin`; checkout `sub/AST-1059/AST-1063-job-carried-rubric-hydration-for-list-columns`; `git merge origin/dev`; `git merge origin/ftr/AST-1059-rubric-grade-displays-jobs-list`; merge-clean gate (`BEHIND=0`, `origin/dev` ancestor of `HEAD`).
2. Do **not** merge or implement AST-1064 UI work on this ref.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Snapshot helper; write `{prefix}_rubric` beside every `{prefix}_grades` save | core |
| `src/ui/api/api_jobs.py` | Flatten `{prefix}_rubric` (+ ensure `{prefix}_score` lift unchanged) on list/detail payloads | ui |

**Out of scope:** `JobsSkipped.tsx` / `JobsInReview.tsx` / `rubricDisplay.ts` grouping or column source switch (AST-1064); Recommended pages; `JOBS_UI_GRADE_RUBRIC` live-artifact map changes unless a one-line comment clarifying “candidate artifact key, not job-carried”; backfill scripts for historical jobs; `tests/` / bible (Betty).

**Contract for AST-1064 (consume only — do not implement here):**

| Section grade field (`JOBS_*_GRADE_FIELD`) | Job-carried rubric key on list JSON | Analysis-time score key(s) |
|-------------------------------------------|-------------------------------------|----------------------------|
| `joblist_grades` | `joblist_rubric` | `joblist_score`, else existing `latest_score` lift |
| `jd_grades` | `jd_rubric` | `jd_score` (+ `latest_score` when set) |
| `get_grades` | `get_rubric` | `get_score` |
| `do_grades` | `do_rubric` | `do_score` |
| `like_grades` | `like_rubric` | `like_score` |

Derive convention: `grade_field.replace("_grades", "_rubric")` / `"_score"`. Do **not** reuse candidate artifact key `jobdesc_rubric` as the job-carried key — job carried is always `jd_rubric`.

Each `*_rubric` value is a **list** of criterion dicts:

```python
{
  "code": str | None,
  "label": str | None,
  "importance": int | float | None,  # as stored on criterion at analysis time
  "grade_descriptions": [{"grade": "A"|"B"|..., "description": str}, ...],
}
```

- **No** `content` field in the snapshot (keep blob size down; descriptions already parsed).
- Absent or empty `*_rubric` means “pre-snapshot job” — AST-1064 may fall back; do not invent live-artifact merge in Ada’s API.

**QA note (Betty):** After land, assert list payloads include `*_rubric` when a fresh grade write runs; assert codes/labels match the criteria used at write (not live candidate after rubric rename); assert scores still flatten. Historical fixture without snapshot: key absent.

---

## Stage 1: Snapshot helper in `consult.py`

**Done when:** A pure helper turns a criteria list into the job-carried shape above; unit-callable with no tracker I/O; criteria with missing `grade_descriptions` get them via `ensure_criterion_grade_table` on a **copy** (do not strip content from the live criteria object used for scoring in the same request).

1. In `src/core/consult.py`, near `_hydrate_grade_reasons_from_rubric`, add:

   ```python
   def _rubric_snapshot_for_job_data(rubric_criteria: list) -> list:
       """Analysis-time rubric criteria for list headers (AST-1063). Omits content."""
   ```

2. Behavior (exact):

   - If `rubric_criteria` is not a list or is empty → return `[]`.
   - For each dict item: shallow-copy the item (or build a new dict); if `grade_descriptions` missing/empty, call `rubric_text.ensure_criterion_grade_table` on the **working copy only** (catch `ValueError` → leave `grade_descriptions` as `[]`).
   - Append `{"code": …, "label": …, "importance": …, "grade_descriptions": …}` only (drop `content` and any other keys).
   - Preserve order of the input criteria list (do not re-sort; UI importance-sort is AST-1064).

⚠️ **Decision:** Snapshot at write time rather than reconstructing from grade `vector` strings alone — codes / importance / grade_descriptions are not on grade rows, and parent AC requires job-carried **hydrated rubric**, not live candidate artifact.

---

## Stage 2: Persist snapshot on every grade write path

**Done when:** Every successful save of `joblist_grades`, `jd_grades`, or `{save_prefix}_grades` also writes the matching `*_rubric` from the **same** `rubric_criteria` / `rubric_list` used for reason hydrate + score in that call. No new transitions; no re-grade of existing jobs.

1. **`_apply_render_verdict_decoded_job`** (get/do/like and any path using it): after building `rubric_criteria` and before/with `save_data`, set:

   ```python
   save_data[f"{prefix}_rubric"] = _rubric_snapshot_for_job_data(rubric_criteria)
   ```

   always when grades are saved (even binary / empty score), so list headers match stored grades for that analysis.

2. **`qualify_job_listings` / `_save_joblist_result`**: when writing `joblist_grades`, also set `joblist_rubric` from the outer `rubric_list` (same list used for `_score_from_grades`). If `rubric_list` is empty, still write `joblist_rubric: []` when grades are written (explicit empty vs key-absent for pre-change data).

3. **`evaluate_jd_batch` `process`**: when writing `jd_grades`, also set `jd_rubric` from the outer `rubric_list` (same rule as joblist).

4. Do **not** change `_render_score`, transition rules, or reason hydration semantics beyond ensuring the snapshot reflects the criteria already in hand.

5. Do **not** backfill historical `job_data` in this ticket.

---

## Stage 3: List / detail API flatten

**Done when:** `GET /api/jobs?view=in_review|skipped|recommended` (and any existing detail path that already uses `_flatten_grades`) lifts `joblist_rubric`, `jd_rubric`, `get_rubric`, `do_rubric`, `like_rubric` to the top-level job object the same way grades/scores are lifted. Score keys already in `_flatten_grades` remain; do not recompute scores from live rubric.

1. In `src/ui/api/api_jobs.py` `_flatten_grades`, extend the key loop (or a second loop) to also lift:

   ```text
   joblist_rubric, jd_rubric, get_rubric, do_rubric, like_rubric
   ```

   from `job_data` when present (same pattern as grades).

2. Keep existing score lift (`*_score` and `latest_score` ← `joblist_score` fallback). **Do not** add live-artifact reading in the API.

3. If a job detail endpoint bypasses `_flatten_grades`, apply the same lift there or route through `_flatten_grades` — grep `get_job` / detail handlers in `api_jobs.py` and match list behavior. Prefer one helper path.

⚠️ **Decision:** Lift on API rather than forcing the UI to dig `job_data.*` — matches current grades flatten and keeps AST-1064 on top-level fields only (`astral.layers.import-direction` / import-discipline).

---

## Stage 4: Manual smoke (builder)

**Done when:** After a local grade write (or unit-level save_job_data of grades+rubric), list JSON shows matching `*_rubric` codes/labels alongside `*_grades` vectors; changing the live candidate rubric in DB **without** re-grading does **not** change the job-carried `*_rubric` on that job.

1. Smoke with one existing consult write path (prefer `grade_like` or `evaluate_jd`) against a temp candidate, or assert via a focused call of `_rubric_snapshot_for_job_data` + `save_job_data` + `_flatten_grades` in a throwaway `debug/spikes/` script (gitignored). Do not commit spike scripts.
2. Confirm AC2 readiness for sibling: `*_score` / `latest_score` still present on flattened jobs when job_data holds them.

---

## Self-Assessment

**Scope:** `Single-Component` — consult grade-write + `api_jobs` flatten only; no list React, no Recommended, no live rubric schema.

**Conf:** `Medium` — write sites are known and few, but parent “already lives” was wrong; historical absence + empty-rubric edge need sibling fallback (documented, not implemented here).

**Risk:** `Medium` — missing a write site leaves some phases without `*_rubric` and AST-1064 still shows dashes for those rows; oversized snapshots if we mistakenly keep `content` (plan omits it).

---

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** One snapshot helper; three call sites (verdict + joblist + jd) instead of three copy-pasted serializers.
- **§2.1 config:** No new config block; grade/rubric key pairing follows existing `save_prefix` / `*_grades` names. Do not dual-source into `JOBS_UI_GRADE_RUBRIC` (that remains candidate artifact ids for other consumers until AST-1064).
- **§2.4 batch:** Snapshot inside existing `process` / verdict paths — no new batch claim loop.
- **§2.6 state machine:** No state/transition changes.
- **§3.3 imports:** `rubric_text.ensure_criterion_grade_table` stays utils→consult; API does not import consult — only lifts stored keys.
- **§3.5 naming:** `*_rubric` parallel to `*_grades` / `*_score`; `jd_rubric` not `jobdesc_rubric` on job payload.
- **import-direction / ui-config-driven:** API shapes job payloads; section→grade_field stays config/manifest; React (sibling) paints resolved shapes without inventing live rubric criteria.

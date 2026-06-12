<!-- linear-archive: AST-352 archived 2026-06-03 -->

## Linear archive (AST-352)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-352/job-modal-updates  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

As Is:
modal popup has an Info tab, plus tabs for all the agent analysis performed.

To Be:

1. Add a tab for the job description text, if it is present for the job.
2. On the analysis tabs, between the header showing the task name + timestamp and the full context of the agent data, display the decoded, job specific analysis performed.
   1. Show the grade first in a color-coded icon
   2. Display the vector title next to the icon
   3. Add a "show rubric" link for each vector that will popup a second modal over the first to display the text in the current rubric for that vector.  We may later want to have the rubric show that was actually sent to the agent, but for now, I think this is cleaner because it's in the database and doesn't need to be parsed from the agent_data.

### Comments

_No comments._

---

# AST-352 — Job Modal Updates

## Plan

Two changes to `JobDetailModal`:

1. Add a **Job Description** side tab (only when `job.job_data.job_description` is already populated — no coat-check trigger on open).
2. On every agent-analysis tab (each entry in `agent_story`), render a **decoded, per-vector analysis header** between the current meta line and the block `TabBar`. Each vector row shows:
   - Color-coded grade icon (A-F / X)
   - Vector label
   - Optional reason (if the task schema included one)
   - A **show rubric** link that opens a second modal over the first, showing the rubric content for that vector from the candidate's stored artifact.

Design choice: resolve the task→grades-key + task→rubric-artifact mapping **at the API layer** (§3.3 — UI business logic lives in the API layer, driven by config), and enrich each `agent_story` entry with the decoded `vector_grades` array and `rubric_artifact` name before returning. The frontend reads grades from the entry directly and pulls rubric content from `CandidateContext` when the link is clicked.

---

### Step 1 — Config: add `scored` flag + `grades_key` + `GRADE_COLORS` to TASK_CONFIG

**File:** `src/utils/config.py` (modify)

- Add `"scored": True` to the five TASK_CONFIG entries that produce displayable per-vector grades: `qualify_job_listings`, `evaluate_jd`, `grade_do`, `grade_get`, `grade_like`. All other tasks (`craft_*`, etc.) get `"scored": False` or simply omit the key (treated as false).
- On those same five entries, add `"grades_key"` — the `job_data` key where grades are stored:
  - `qualify_job_listings` → `"grades_key": "joblist_grades"`
  - `evaluate_jd` → `"grades_key": "jd_grades"`
  - `grade_do` → `"grades_key": "do_grades"`
  - `grade_get` → `"grades_key": "get_grades"`
  - `grade_like` → `"grades_key": "like_grades"`
- `rubric_artifact` already exists in `CONSULT_CONFIG` per task. Mirror it onto these five `TASK_CONFIG` entries so all display metadata is collocated with the task definition. Copy the values:
  - `qualify_job_listings` → `"rubric_artifact": "joblist_rubric"`
  - `evaluate_jd` → `"rubric_artifact": "jobdesc_rubric"`
  - `grade_do` → `"rubric_artifact": "do_rubric"`
  - `grade_get` → `"rubric_artifact": "get_rubric"`
  - `grade_like` → `"rubric_artifact": "like_rubric"`
- Add `GRADE_COLORS` dict near the top of config (with the other shared constants), sourced directly from the existing HTML report stylesheet:
  ```python
  GRADE_COLORS = {
      "A": "#28a745",
      "B": "#ffc107",
      "C": "#fd7e14",
      "D": "#dc3545",
      "F": "#8b0000",
      "X": "#a78bfa",
  }
  ```
- No new helper function needed — callers use `TASK_CONFIG[task_key].get("scored")` directly.
- No changes to `CONSULT_CONFIG` structure (rubric_artifact stays there for the consult flow), `JOB_STATES`, or `TRACKER_CONFIG`.

### Step 2 — Core: enrich agent_story with decoded analysis + filter RESPONSE blocks

**File:** `src/core/roster.py` (modify `get_entity_agent_story`)

**Grades enrichment** — for each entry in `agent_responses`:
- Look up `task_cfg = TASK_CONFIG.get(entry["task_key"], {})`.
- If `task_cfg.get("scored")` is truthy, pull `vector_grades = entity.get("job_data", {}).get(task_cfg["grades_key"])` and attach two new fields to the enriched entry:
  - `vector_grades`: the list of `{vector, grade, reason?}` dicts (may be `None` if grading never ran yet).
  - `rubric_artifact`: string name, e.g. `"get_rubric"`.

**RESPONSE block content filtering** — for scored tasks, after block content is fetched from `data_map`, for any block typed `"RESPONSE"`:
1. Try to parse `content` as JSON.
2. If the parsed result has a `"jobs"` array (batch tasks: `qualify_job_listings`, `evaluate_jd`):
   - Check whether any item has `"astral_job_id"`. If none do → old encoded data; set `content = ""` (frontend skips rendering it).
   - If `astral_job_id` is present → filter to the single entry matching `entity["astral_job_id"]` and replace `content` with `json.dumps(match, indent=2)`. If no match (job was missing from this batch run), set `content = ""`.
3. If the parsed result has no `"jobs"` key (single-job tasks: `grade_do`/`grade_get`/`grade_like`) → show the response as-is; it's already scoped to this job.
4. If content can't be parsed as JSON at all → leave unchanged.

This keeps all filtering server-side; the frontend is dumb and just displays whatever content arrives (or nothing if content is empty).

**No new DB calls** — all data is already on the job row and in the already-fetched `data_map`.

### Step 3 — UI: show Job Description tab when present

**File:** `src/ui/frontend/src/components/JobDetailModal.tsx` (modify)

- Derive `hasJD = Boolean(job.job_data?.job_description)`.
- Insert a new tab with `id: "__jd__"`, `label: "Job Description"` immediately after `__info__` when `hasJD` is true.
- In `renderSideContent`, handle `"__jd__"` by rendering a `<div>` with the job description text, normalized and styled with `white-space: pre-wrap` (preserves intentional line breaks, wraps for readability, collapses excess whitespace). Add class `.entity-jd-content` to `App.css`.

### Step 4 — UI: decoded analysis header in AgentStoryTab

**File:** `src/ui/frontend/src/components/AgentStoryTab.tsx` (modify)

- Extend `AgentStoryEntry` with the two optional fields emitted by Step 2:
  ```ts
  vector_grades?: Array<{ vector: string; grade: string; reason?: string }>
  rubric_artifact?: string
  ```
- Between `entity-story-meta` and the block `TabBar`, render a new `<AgentAnalysisHeader>` component when `entry.vector_grades` is non-empty.

### Step 5 — New component: `AgentAnalysisHeader`

**File:** `src/ui/frontend/src/components/AgentAnalysisHeader.tsx` (new)

- Props:
  ```ts
  {
    grades: Array<{ vector: string; grade: string; reason?: string }>
    rubricArtifact?: string   // e.g. "get_rubric"
  }
  ```
- Renders one row per vector:
  - Grade dot/badge (span with class `grade-dot dot-{a|b|c|d|f|x}`) matching the HTML report's existing `.grade-dot` pattern and colors.
  - Vector label.
  - `reason` in muted text (only if present).
  - A `show rubric` link that calls `setRubricVector(v.vector)` to open the nested modal.
- Reads the candidate via `useCandidate()` and pulls `candidate_data.artifacts[rubricArtifact]` (a list of `{label, content}`). Finds the entry where `label === vector` and passes its `content` to `<RubricModal>`.
- Renders a nested `<RubricModal>` when a vector is selected.

### Step 6 — New component: `RubricModal`

**File:** `src/ui/frontend/src/components/RubricModal.tsx` (new)

- Small wrapper around the existing `<Modal>` component. Props:
  ```ts
  { open: boolean; onClose: () => void; vector: string; content: string | null }
  ```
- Title: `Rubric — {vector}`. Body: `<div>` with `white-space: pre-wrap` showing the rubric content; falls back to `"No rubric found for this vector."` if content is null.
- Because `Modal` already portals to `document.body`, stacking works automatically. Pass `stacked` to `<Modal>` to apply a higher z-index.

### Step 7 — Modal stacking support

**File:** `src/ui/frontend/src/components/Modal.tsx` + `src/ui/frontend/src/App.css` (modify)

- Add `stacked?: boolean` to `ModalProps`; when true, attach `modal-overlay--stacked` class to the overlay div.
- Add `.modal-overlay--stacked { z-index: 2000 }` rule in section 9 (Modal) of `App.css`.
- `RubricModal` passes `stacked`; primary `JobDetailModal` does not.

### Step 8 — Styling: grade dots + analysis rows + JD content

**File:** `src/ui/frontend/src/App.css` (modify)

- Add CSS variables for grade colors (matching `GRADE_COLORS` in config) to `:root`:
  ```css
  --grade-a: #28a745;
  --grade-b: #ffc107;
  --grade-c: #fd7e14;
  --grade-d: #dc3545;
  --grade-f: #8b0000;
  --grade-x: #a78bfa;
  ```
- Add `.grade-dot` base style (circular badge ~20px, centered letter, dark text on colored bg) and `.dot-a` through `.dot-x` using the CSS vars — mirrors the HTML report's `.grade-dot` pattern.
- Add `.analysis-header`, `.analysis-row`, `.analysis-vector`, `.analysis-reason`, `.analysis-rubric-link` classes to match existing `entity-story-*` naming.
- Add `.entity-jd-content` — scrollable, `white-space: pre-wrap`, inherits body font (not monospace), same padding/bg as `entity-story-content`.
- Add `.modal-overlay--stacked { z-index: 2000 }`.

---

### Files Changed

| File | Change |
|------|--------|
| `src/utils/config.py` | Add `scored`, `grades_key`, `rubric_artifact` to 5 scored TASK_CONFIG entries; add `GRADE_COLORS` constant |
| `src/core/roster.py` | Enrich each `agent_story` entry with `vector_grades` + `rubric_artifact` for scored tasks |
| `src/ui/frontend/src/components/JobDetailModal.tsx` | Conditionally insert Job Description tab after Info |
| `src/ui/frontend/src/components/AgentStoryTab.tsx` | Extend interface; render `<AgentAnalysisHeader>` |
| `src/ui/frontend/src/components/AgentAnalysisHeader.tsx` | **New** — renders per-vector grade dots + reason + show-rubric links |
| `src/ui/frontend/src/components/RubricModal.tsx` | **New** — stacked modal showing rubric content for one vector |
| `src/ui/frontend/src/components/Modal.tsx` | Add optional `stacked` prop for elevated z-index |
| `src/ui/frontend/src/App.css` | Grade color CSS vars, `.grade-dot` styles, analysis row styles, `.entity-jd-content`, stacked modal z-index |

---

### Resolved decisions

1. **Grade colors** — from HTML report stylesheet: A=#28a745, B=#ffc107, C=#fd7e14, D=#dc3545, F=#8b0000, X=#a78bfa. Stored in `GRADE_COLORS` in `config.py`; mirrored as CSS vars in `App.css`.
2. **JD tab content** — `white-space: pre-wrap` in a `<div>` (preserves line breaks, wraps for prose readability, collapses excess whitespace). No `<pre>` / monospace.
3. **Craft tasks** — `scored: False` (or omitted). `craft_job_resume` and siblings produce no displayable job-data grades. Analysis header skipped for these tabs entirely.
4. **Dumb UI** — all task→mapping logic resolved on the backend; frontend reads `vector_grades` and `rubric_artifact` directly from the enriched agent_story entry.
5. **Rubric label matching** — match `label === vector` in the artifact list. Silent "no rubric found" fallback if labels drift.

---

## Review Against ASTRAL_CODE_RULES

- **§1.3 DRY** — Reusing `<Modal>` for the stacked rubric popup (just a `stacked` flag). New `AgentAnalysisHeader` extracted as its own component so `AgentStoryTab` stays focused.
- **§1.4 No hardcoded sets** — `scored`, `grades_key`, `rubric_artifact` live in TASK_CONFIG; `GRADE_COLORS` in config. No magic dicts in core or UI code.
- **§2.1 Config as source of truth** — `GRADE_COLORS` in `config.py` is the canonical source; CSS vars in `App.css` use the same values. `scored` flag in TASK_CONFIG drives backend enrichment logic.
- **§3.3 Layer rules** — backend enrichment in `src/core/roster.py` (core), reads already-loaded job data (no new DB call). `src/utils/config.py` gains only constants/data (pure utils — safe). API layer (`src/ui/api/api_jobs.py`) untouched. UI imports only contexts and sibling components.
- **§3.3 UI business logic in API layer** — rubric-artifact name and grades resolved server-side; frontend is purely presentational.
- **§3.5 Naming conventions** — `AgentAnalysisHeader.tsx`, `RubricModal.tsx` PascalCase. No new API routes. No Python naming changes.
- **§2.4 / §2.6** — not applicable.

No rule conflicts identified. Ready for review.

---

## Review

**Commit:** `4752ee0`
**Branch:** `dev`
